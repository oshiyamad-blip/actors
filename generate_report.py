import json

def generate_text_report():
    input_file = "cinepu_latest.json"
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
    except Exception as e:
        print(f"Error loading {input_file}: {e}")
        return

    # Filter paid jobs
    paid_items = [i for i in items if i.get('is_paid')]
    
    report = "【エージェントAI】最新のオーディション案件（報酬あり） サマリー\n"
    report += "="*50 + "\n\n"
    report += f"シネマプランナーズから、新しい「報酬あり」案件が {len(paid_items)} 件見つかりました。\n\n"
    
    for idx, item in enumerate(paid_items[:10], 1):  # show top 10
        report += f"{idx}. {item['title']}\n"
        report += f"   - タグ: {item['tags']}\n"
        report += f"   - 投稿日: {item['date']}\n"
        report += f"   - URL: {item['url']}\n\n"
        
    if len(paid_items) > 10:
        report += f"...他 {len(paid_items) - 10} 件の報酬あり案件があります。\n"
        
    report += "="*50 + "\n"
    report += "引き続き、優良な案件のみをスクリーニングして報告します。\n"

    with open("report_body.txt", 'w', encoding='utf-8') as f:
        f.write(report)
        
    print("Report generated at report_body.txt")

if __name__ == "__main__":
    generate_text_report()
