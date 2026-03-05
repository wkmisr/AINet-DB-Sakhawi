import streamlit as st
import google.generativeai as genai
import json

# 1. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="AINet-DB AI Editor", layout="wide")
st.title("🌙 AINet-DB AI-Assisted Editor")

# 2. セッション状態の管理
if 'data' not in st.session_state:
    st.session_state.data = {
        "aind_id": "", "original_id": "", "name": "", "death_year": 850,
        "teachers": [], "family": [], "institutions": []
    }

col1, col2 = st.columns([1, 1.5])

# --- 左カラム：AI解析 ---
with col1:
    st.header("1. 原文解析")
    source_text = st.text_area("サハウィーのテキストを貼り付け", height=400)
    
    if st.button("✨ AIで項目を詳細抽出"):
        if source_text:
            with st.spinner("AIが詳細データを解析中..."):
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    selected_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
                    model = genai.GenerativeModel(selected_model)
                    
                    prompt = f"""
                    以下のアラビア語テキストから人物情報を抽出し、必ず以下のJSON形式のみで返してください。
                    「###$数字$# $」があればoriginal_idとして抽出。
                    関係性や性別はテキストから推測してください。
                    {{
                      "original_id": "数字",
                      "name": "姓名",
                      "death_year": 数字,
                      "teachers": [ {{"name": "名前", "gender": "男性/女性"}} ],
                      "family": [ {{"name": "名前", "gender": "男性/女性", "relation": "親/子/兄弟/夫婦/従弟/その他"}} ],
                      "institutions": [ {{"name": "施設名", "relation": "創設者/教えていた/学んでいた/その他"}} ]
                    }}
                    テキスト：{source_text}
                    """
                    response = model.generate_content(prompt)
                    res_text = response.text.strip().replace("```json", "").replace("```", "")
                    st.session_state.data.update(json.loads(res_text))
                    st.success("抽出成功！")
                except Exception as e:
                    st.error(f"解析エラー: {e}")

# --- 右カラム：データ編集 ---
with col2:
    st.header("2. データ詳細編集")
    d = st.session_state.data
    
    # ID & 基本情報
    c_id1, c_id2 = st.columns(2)
    d["aind_id"] = c_id1.text_input("AIND ID", value=d.get("aind_id", ""))
    d["original_id"] = c_id2.text_input("Original ID", value=d.get("original_id", ""))
    d["name"] = st.text_input("フルネーム", value=d.get("name", ""))
    
    c_y1, c_y2 = st.columns(2)
    d["death_year"] = c_y1.number_input("没年 (Hijri)", value=int(d.get("death_year", 850)))
    c_y2.metric("西暦 (目安)", f"約 {int(d['death_year'] * 0.97 + 622)} 年")

    st.divider()

    # --- 師匠セクション ---
    st.subheader("🎓 師匠 (Teachers)")
    for i, t in enumerate(d.get("teachers", [])):
        cols = st.columns([3, 2, 1])
        t["name"] = cols[0].text_input(f"師匠名 {i}", value=t.get("name", ""), key=f"tn_{i}")
        t["gender"] = cols[1].selectbox(f"性別", ["男性", "女性"], index=0 if t.get("gender")=="男性" else 1, key=f"tg_{i}")
        if cols[2].button("❌", key=f"tdel_{i}"):
            d["teachers"].pop(i); st.rerun()
    if st.button("＋ 師匠を追加"):
        d["teachers"].append({"name": "", "gender": "男性"}); st.rerun()

    st.divider()

    # --- 家族セクション ---
    st.subheader("👪 家族 (Family)")
    rel_options = ["親", "子", "兄弟", "夫婦", "従弟", "その他"]
    for i, f in enumerate(d.get("family", [])):
        cols = st.columns([3, 2, 2, 1])
        f["name"] = cols[0].text_input(f"家族名 {i}", value=f.get("name", ""), key=f"fn_{i}")
        f["gender"] = cols[1].selectbox(f"性別", ["男性", "女性"], index=0 if f.get("gender")=="男性" else 1, key=f"fg_{i}")
        idx = rel_options.index(f["relation"]) if f.get("relation") in rel_options else 5
        f["relation"] = cols[2].selectbox(f"関係", rel_options, index=idx, key=f"fr_{i}")
        if cols[3].button("❌", key=f"fdel_{i}"):
            d["family"].pop(i); st.rerun()
    if st.button("＋ 家族を追加"):
        d["family"].append({"name": "", "gender": "男性", "relation": "その他"}); st.rerun()

    st.divider()

    # --- 施設セクション ---
    st.subheader("🕌 関連施設 (Institutions)")
    inst_rel_options = ["創設者", "教えていた", "学んでいた", "その他"]
    for i, inst in enumerate(d.get("institutions", [])):
        cols = st.columns([3, 3, 1])
        inst["name"] = cols[0].text_input(f"施設名 {i}", value=inst.get("name", ""), key=f"in_{i}")
        idx = inst_rel_options.index(inst["relation"]) if inst.get("relation") in inst_rel_options else 3
        inst["relation"] = cols[1].selectbox(f"関係性", inst_rel_options, index=idx, key=f"ir_{i}")
        if cols[2].button("❌", key=f"idel_{i}"):
            d["institutions"].pop(i); st.rerun()
    if st.button("＋ 施設を追加"):
        d["institutions"].append({"name": "", "relation": "学んでいた"}); st.rerun()

    st.divider()
    
    # XML出力
    if st.checkbox("XMLプレビューを表示"):
        st.code(f"""<person id="{d['aind_id']}" original_id="{d['original_id']}">
    <name>{d['name']}</name>
    <death>{d['death_year']}</death>
    <teachers>
        {" ".join([f'<teacher gender="{t["gender"]}">{t["name"]}</teacher>' for t in d["teachers"] if t["name"]])}
    </teachers>
    <family>
        {" ".join([f'<member gender="{f["gender"]}" relation="{f["relation"]}">{f["name"]}</member>' for f in d["family"] if f["name"]])}
    </family>
    <institutions>
        {" ".join([f'<inst relation="{ins["relation"]}">{ins["name"]}</inst>' for ins in d["institutions"] if ins["name"]])}
    </institutions>
</person>""", language="xml")
