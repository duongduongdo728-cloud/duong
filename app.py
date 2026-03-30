import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

st.set_page_config(page_title="News Monitor", layout="wide")
st.title("News Monitor")

TOPIC_ORDER = [
    "Trong nước - Lãi suất & Thanh khoản",
    "Trong nước - Chính sách tiền tệ",
    "Trong nước - Chính sách tài khóa & đầu tư công",
    "Trong nước - Quy định & pháp lý",
    "Trong nước - Tỷ giá & Ngoại hối",
    "Trong nước - Kinh tế vĩ mô Việt Nam",
    "Trong nước - KQKD doanh nghiệp Việt Nam Q1/2026",
    "Trong nước - Đại hội cổ đông doanh nghiệp Việt Nam",
    "Quốc tế - Ngân hàng trung ương",
    "Quốc tế - Địa chính trị & xung đột",
    "Quốc tế - AI & tác động đầu tư",
    "Khác"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def classify_content(title, summary, source):
    text = f"{title} {summary} {source}".lower()

    # Trong nước
    if any(k in text for k in ["sbv", "nhnn", "vietstock", "vietnam", "viet nam", "vietcombank", "bidv", "vietinbank", "agribank"]):
        if any(k in text for k in [
            "vnibor", "omo", "liquidity", "thanh khoản", "interbank", "repo",
            "interest rate", "lãi suất", "deposit rate", "lending rate"
        ]):
            return "Trong nước - Lãi suất & Thanh khoản"

        if any(k in text for k in [
            "monetary policy", "chính sách tiền tệ", "credit growth", "room tín dụng",
            "policy rate", "điều hành tiền tệ", "money supply"
        ]):
            return "Trong nước - Chính sách tiền tệ"

        if any(k in text for k in [
            "fiscal policy", "chính sách tài khóa", "public investment", "đầu tư công",
            "budget", "ngân sách", "infrastructure"
        ]):
            return "Trong nước - Chính sách tài khóa & đầu tư công"

        if any(k in text for k in [
            "regulation", "quy định", "decree", "nghị định", "circular", "thông tư",
            "law", "luật", "legal", "pháp lý"
        ]):
            return "Trong nước - Quy định & pháp lý"

        if any(k in text for k in [
            "usd/vnd", "eur/vnd", "jpy/vnd", "cny/vnd",
            "exchange rate", "tỷ giá", "forex", "ngoại hối"
        ]):
            return "Trong nước - Tỷ giá & Ngoại hối"

        if any(k in text for k in [
            "retail", "bán lẻ", "consumption", "tiêu dùng", "fdi",
            "export", "xuất khẩu", "import", "nhập khẩu",
            "inflation", "lạm phát", "cpi", "gdp", "economic growth"
        ]):
            return "Trong nước - Kinh tế vĩ mô Việt Nam"

        if any(k in text for k in [
            "q1 2026", "quý 1/2026", "earnings", "kết quả kinh doanh",
            "profit", "lợi nhuận", "revenue", "doanh thu", "financial results"
        ]):
            return "Trong nước - KQKD doanh nghiệp Việt Nam Q1/2026"

        if any(k in text for k in [
            "agm", "đại hội cổ đông", "annual general meeting",
            "dividend", "cổ tức", "capital increase", "tăng vốn", "shareholder meeting"
        ]):
            return "Trong nước - Đại hội cổ đông doanh nghiệp Việt Nam"

    # Quốc tế
    if any(k in text for k in [
        "federal reserve", "fed", "ecb", "boj", "pboc", "boe", "central bank",
        "rate hike", "rate cut", "policy decision"
    ]):
        return "Quốc tế - Ngân hàng trung ương"

    if any(k in text for k in [
        "war", "conflict", "geopolitical", "sanction", "tariff",
        "ukraine", "russia", "middle east", "taiwan", "trade war"
    ]):
        return "Quốc tế - Địa chính trị & xung đột"

    if any(k in text for k in [
        "artificial intelligence", " ai ", "generative ai", "semiconductor",
        "chip", "gpu", "datacenter", "automation", "productivity"
    ]):
        return "Quốc tế - AI & tác động đầu tư"

    return "Khác"

def deduplicate(items):
    seen = set()
    result = []
    for item in items:
        key = (item["title"].lower(), item["link"].lower())
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

def scrape_reuters():
    items = []
    urls = [
        "https://www.reuters.com/world/",
        "https://www.reuters.com/markets/",
        "https://www.reuters.com/business/"
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")

            for a in soup.find_all("a", href=True):
                title = clean_text(a.get_text())
                href = a["href"]

                if not title or len(title) < 25:
                    continue

                if href.startswith("/"):
                    link = "https://www.reuters.com" + href
                elif href.startswith("http"):
                    link = href
                else:
                    continue

                topic = classify_content(title, "", "Reuters")

                items.append({
                    "title": title,
                    "summary": "",
                    "source": "Reuters",
                    "link": link,
                    "published": "",
                    "topic": topic
                })
        except Exception:
            pass

    return items

def scrape_bloomberg():
    items = []
    urls = [
        "https://www.bloomberg.com/markets",
        "https://www.bloomberg.com"
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")

            for a in soup.find_all("a", href=True):
                title = clean_text(a.get_text())
                href = a["href"]

                if not title or len(title) < 25:
                    continue

                if href.startswith("/"):
                    link = "https://www.bloomberg.com" + href
                elif href.startswith("http"):
                    link = href
                else:
                    continue

                topic = classify_content(title, "", "Bloomberg")

                items.append({
                    "title": title,
                    "summary": "",
                    "source": "Bloomberg",
                    "link": link,
                    "published": "",
                    "topic": topic
                })
        except Exception:
            pass

    return items

def scrape_sbv():
    items = []
    urls = [
        "https://www.sbv.gov.vn/webcenter/portal/vi/menu/trangchu",
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")

            for a in soup.find_all("a", href=True):
                title = clean_text(a.get_text())
                href = a["href"]

                if not title or len(title) < 20:
                    continue

                if href.startswith("/"):
                    link = "https://www.sbv.gov.vn" + href
                elif href.startswith("http"):
                    link = href
                else:
                    continue

                topic = classify_content(title, "", "SBV")

                items.append({
                    "title": title,
                    "summary": "",
                    "source": "SBV",
                    "link": link,
                    "published": "",
                    "topic": topic
                })
        except Exception:
            pass

    return items

def scrape_vietstock():
    items = []
    urls = [
        "https://vietstock.vn/",
        "https://vietstock.vn/kinh-te.htm",
        "https://vietstock.vn/tai-chinh.htm"
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")

            for a in soup.find_all("a", href=True):
                title = clean_text(a.get_text())
                href = a["href"]

                if not title or len(title) < 20:
                    continue

                if href.startswith("/"):
                    link = "https://vietstock.vn" + href
                elif href.startswith("http"):
                    link = href
                else:
                    continue

                topic = classify_content(title, "", "Vietstock")

                items.append({
                    "title": title,
                    "summary": "",
                    "source": "Vietstock",
                    "link": link,
                    "published": "",
                    "topic": topic
                })
        except Exception:
            pass

    return items

if st.button("Tải tin mới nhất"):
    with st.spinner("Đang tải tin..."):
        all_items = []
        all_items.extend(scrape_sbv())
        all_items.extend(scrape_vietstock())
        all_items.extend(scrape_reuters())
        all_items.extend(scrape_bloomberg())

        all_items = deduplicate(all_items)

        st.success(f"Tải được {len(all_items)} tin.")

        grouped = {topic: [] for topic in TOPIC_ORDER}
        for item in all_items:
            grouped[item["topic"]].append(item)

        for topic in TOPIC_ORDER:
            if grouped[topic]:
                st.subheader(topic)
                for article in grouped[topic]:
                    with st.expander(article["title"]):
                        st.write(f"**Nguồn:** {article['source']}")
                        if article["published"]:
                            st.write(f"**Thời gian:** {article['published']}")
                        if article["summary"]:
                            st.write(f"**Tóm tắt:** {article['summary']}")
                        st.markdown(f"[Đọc bài đầy đủ]({article['link']})")