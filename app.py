import streamlit as st
import google.generativeai as genai
import json
import requests
import base64

# 1. APIキー・GitHubトークンの設定
api_key = st.secrets.get("GEMINI_API_KEY")
github_token = st.secrets.get("GITHUB_TOKEN")
# ↓ あなたのGitHubユーザー名とレポジトリ名に変更してください
repo_name = "YOUR_GITHUB_NAME/YOUR_REPO_NAME" 

if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB TEI Editor", layout="wide")

# --- CSS (アラビア語の可読性とUI) ---
st.markdown("""
    <style>
    textarea { font-size: 22px !important; line-height: 2.0 !important; font-family: 'Amiri', serif; }
    .translation-box { font-size: 18px; line-height: 1.8; background-color: #f8f9fa; padding: 25px; border-left: 5px solid #007bff; border-radius: 10px; margin-bottom: 25px; color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 AINet-DB AI-Assisted TEI Editor")

# 確信度の選択肢
CERT_OPTIONS = ["High", "Medium", "Low", "Unknown"]

# 2. セッション状態の初期化
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "", "original_id": "", "name": "", "name_cert": "High",
        "death_year": 850, "death_cert": "High",
        "teachers": [], "family": [], "institutions": [], 
        "source_text": "", "translation": ""
    }

col1, col2 = st.columns([1, 1.3])

# --- 左カラム：ソース解析 ---
with col1:
    st.header("1. Source Text Analysis")
    source_text = st.text_area("Paste Arabic text here", height=450)
    
    if st.button("✨ AI Analysis (Data + Translation)"):
        if source_text:
            st.session_state.data["source_text"] = source_text
            with st.spinner("Analyzing and translating..."):
                try:
                    # モデル名の自動判別ロジック
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    Analyze the Arabic text and return ONLY JSON.
                    Translate metadata (gender, relation) into English.
                    Estimate 'cert' (High, Medium, Low) for each field.
                    
                    JSON Format:
                    {{
                      "original_id": "string",
                      "name": "Arabic full name", "name_cert": "High/Medium/Low",
                      "death_year": number, "death_cert": "High/Medium/Low",
                      "teachers": [ {{"name": "name", "gender": "Male/Female", "cert": "High/Medium/Low"}} ],
                      "family": [ {{"name": "name", "gender": "Male/Female", "relation": "Parent/Child/Sibling/Spouse/Cousin/Other", "cert": "High/Medium/Low"}} ],
                      "institutions": [ {{"name": "name", "relation": "Founder/Instructor/Student/Other", "cert": "High/Medium/Low"}} ],
                      "japanese_translation": "全文の日本語訳"
                    }}
                    Text: {source_text}
                    """
                    response = model.generate_content(prompt)
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    new_data = json.loads(res_text)
                    
                    if not isinstance(new_data.get("death_year"), (int, float)):
                        new_data["death_year"] = 850
                    
                    st.session_state.data.update(new_data)
                    st.session_state.data["translation"] = new_data.get("japanese_translation", "")
                    st.success("Analysis complete!")
                except Exception as e:
                    st.error(f"Analysis Error: {e}")

    if st.session_state.data["translation"]:
        st.subheader("🇯🇵 Japanese Translation")
        st.markdown(f'<div class="translation-box">{st.session_state.data["translation"]}</div>', unsafe_allow_html=True)

# --- 右カラム：データ編集とGitHub送信 ---
with col2:
    st.header("2. TEI Data Editor")
    d = st.session_state.data
    
    # ID & 姓名
    c_id_1, c_id_2 = st.columns(2)
    d["aind_id"] = c_id_1.text_input("AIND ID", value=d.get("aind_id", ""))
    d["original_id"] = c_id_2.text_input("Original ID", value=d.get("original_id", ""))
    
    c_name, c_ncert = st.columns([3, 1])
    d["name"] = c_name.text_input("Full Name (Arabic)", value=d.get("name", ""))
    d["name_cert"] = c_ncert.selectbox("Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(d.get("name_cert", "High")), key="ncert")
    
    # 没年
    c_death, c_dcert, c_ad = st.columns([2, 1, 1])
    try: death_val = int(d.get("death_year", 850))
    except: death_val = 850
    d["death_year"] = c_death.number_input("Death (Hijri AH)", value=death_val)
    d["death_cert"] = c_dcert.selectbox("Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(d.get("death_cert", "High")), key="dcert")
    c_ad.metric("AD (Approx)", f"ca. {int(d['death_year'] * 0.97 + 622)}")

    st.divider()

    # --- 師匠 / 家族 / 施設 編集セクション ---
    for section, label, key_prefix in [("teachers", "🎓 Teachers", "tn"), ("family", "👪 Family", "fn"), ("institutions", "🕌 Institutions", "in")]:
        st.subheader(label)
        items = d.get(section, [])
        for i, item in enumerate(items):
            n_cols = 4 if section == "family" else 3
            cols = st.columns([2.5, 1.5, 1.5, 1.5, 0.5] if n_cols==4 else [3, 2, 2, 0.5])
            item["name"] = cols[0].text_input("Name", value=item.get("name", ""), key=f"{key_prefix}n_{i}")
            if "gender" in item:
                item["gender"] = cols[1].selectbox("Sex", ["Male", "Female"], index=0 if item.get("gender")=="Male" else 1, key=f"{key_prefix}g_{i}")
            if section == "family":
                rel_f = ["Parent", "Child", "Sibling", "Spouse", "Cousin", "Other"]
                item["relation"] = cols[2].selectbox("Rel", rel_f, index=rel_f.index(item.get("relation", "Other")) if item.get("relation") in rel_f else 5, key=f"{key_prefix}r_{i}")
            if section == "institutions":
                rel_i = ["Founder", "Instructor", "Student", "Other"]
                item["relation"] = cols[1].selectbox("Role", rel_i, index=rel_i.index(item.get("relation", "Other")) if item.get("relation") in rel_i else 3, key=f"{key_prefix}r_{i}")
            
            item["cert"] = cols[-2].selectbox("Cert", CERT_OPTIONS, index=CERT_OPTIONS.index(item.get("cert", "High")) if item.get("cert") in CERT_OPTIONS else 0, key=f"{key_prefix}c_{i}")
            if cols[-1].button("❌", key=f"{key_prefix}d_{i}"):
                items.pop(i); st.rerun()
        if st.button(f"＋ Add {section.capitalize()}", key=f"add_{section}"):
            new_item = {"name": "", "cert": "High"}
            if "teachers" in section: new_item["gender"] = "Male"
            if "family" in section: new_item.update({"gender": "Male", "relation": "Other"})
            if "institutions" in section: new_item["relation"] = "Student"
            items.append(new_item); st.rerun()
        st.divider()

    # --- TEI XML生成 (属性準拠) ---
    xml_output = f"""<person xml:id="{d['aind_id']}" source="#original_{d['original_id']}" cert="{d['name_cert'].lower()}">
    <persName xml:lang="ar" type="full">{d['name']}</persName>
    <death calendar="hijri" when-custom="{d['death_year']}" cert="{d['death_cert'].lower()}">{d['death_year']}</death>
    <listBibl type="teachers">
        {" ".join([f'<person sex="{t["gender"][0]}" role="teacher" cert="{t.get("cert", "High").lower()}"><persName>{t["name"]}</persName></person>' for t in d["teachers"] if t["name"]])}
    </listBibl>
    <listRelation type="family">
        {" ".join([f'<relation active="#this" passive="{f["name"]}" name="{f.get("relation", "Other").lower()}" sex="{f["gender"][0]}" cert="{f.get("cert", "High").lower()}"/>' for f in d["family"] if f["name"]])}
    </listRelation>
    <listOrg type="institutions">
        {" ".join([f'<orgName role="{ins.get("relation", "Other").lower()}" cert="{ins.get("cert", "High").lower()}">{ins["name"]}</orgName>' for ins in d["institutions"] if ins["name"]])}
    </listOrg>
    <note type="description">
{d['source_text']}
    </note>
</person>"""

    if st.checkbox("Show Final TEI XML Preview"):
        st.code(xml_output, language="xml")

    # --- GitHub送信 ---
    st.subheader("🚀 GitHub Deployment")
    f_path = st.text_input("File Path", value=f"data/{d['aind_id'] or 'temp'}.xml")
    
    if st.button("⬆️ Send to GitHub"):
        if not github_token:
            st.error("GitHub Token is missing in Secrets!")
        else:
            url = f"https://api.github.com/repos/{repo_name}/contents/{f_path}"
            headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
            res = requests.get(url, headers=headers)
            sha = res.json().get("sha") if res.status_code == 200 else None
            payload = {"message": f"Update {d['name']}", "content": base64.b64encode(xml_output.encode()).decode(), "sha": sha}
            put_res = requests.put(url, headers=headers, json=payload)
            if put_res.status_code in [200, 201]:
                st.success(f"Deployed: {f_path}")
            else:
                st.error(f"Error: {put_res.json().get('message')}")
