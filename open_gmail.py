import urllib.parse
import webbrowser

def open_gmail():
    with open('report_body.txt', 'r', encoding='utf-8') as f:
        body = f.read()

    subject = "【エージェントAI】最新のオーディション案件（報酬あり）"
    body_encoded = urllib.parse.quote(body)
    subject_encoded = urllib.parse.quote(subject)

    url = f"https://mail.google.com/mail/?view=cm&fs=1&to=&su={subject_encoded}&body={body_encoded}"
    webbrowser.open(url)
    print("Opened Gmail compose window")

if __name__ == "__main__":
    open_gmail()
