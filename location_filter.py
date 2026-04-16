def is_valid_location(text):
    """
    Returns True if the text indicates Tokyo/suburbs or is completely unspecified.
    Returns False if it's strictly a local regional project outside Tokyo.
    """
    good_keywords = ["東京", "都内", "神奈川", "千葉", "埼玉", "関東", "全国"]
    bad_keywords = [
        "北海道", "青森", "岩手", "宮城", "秋田", "山形", "福島", "東北",
        "新潟", "富山", "石川", "福井", "山梨", "長野", "岐阜", "静岡", "愛知", "名古屋",
        "三重", "滋賀", "京都", "大阪", "関西", "兵庫", "奈良", "和歌山",
        "鳥取", "島根", "岡山", "広島", "山口", "中国",
        "徳島", "香川", "愛媛", "高知", "四国",
        "福岡", "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄", "九州"
    ]
    
    if any(k in text for k in good_keywords):
        return True
        
    if any(k in text for k in bad_keywords):
        return False
        
    return True
