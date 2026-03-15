import sys, json, os, qrcode

SECRET_PASS = "5698"
GH_USER = "dipindipz"
GH_REPO = "Pookkalasham"

# ---------------- AUTH ----------------
def check_auth():
    if input("🔑 Admin Password: ") != SECRET_PASS:
        print("\033[91mUnauthorized\033[0m")
        sys.exit()

# ---------------- DATABASE ----------------
def load_db():
    if not os.path.exists("ledger.json"):
        return {"title":"POOKKALASHAM LEDGER","data":[]}
    with open("ledger.json","r") as f:
        return json.load(f)

def save_db(db):
    with open("ledger.json","w") as f:
        json.dump(db,f,indent=4)

# ---------------- WEB UPDATE ----------------
def update_web(db):

    total = sum(i[1] for i in db["data"])
    paid = sum(i[1] for i in db["data"] if i[2])
    percent = int((paid/total)*100) if total>0 else 0

    html = f"""
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{{font-family:sans-serif;background:#111;color:white;padding:20px}}
.card{{background:#1e1e1e;padding:20px;border-radius:10px;max-width:500px;margin:auto}}
.bar{{background:#333;height:12px;border-radius:10px}}
.fill{{background:#2ecc71;height:12px;width:{percent}%}}
table{{width:100%;margin-top:20px}}
td{{padding:10px;border-bottom:1px solid #333}}
</style>
</head>

<body>
<div class="card">

<h2>{db["title"]}</h2>

<p>Collection ₹{paid} / ₹{total}</p>

<div class="bar">
<div class="fill"></div>
</div>

<table>
"""

    for name,amt,status in db["data"]:
        s="✔ PAID" if status else "⏳ PENDING"
        html+=f"<tr><td>{name}<br><small>₹{amt}</small></td><td>{s}</td></tr>"

    html+="</table></div></body></html>"

    with open("index.html","w") as f:
        f.write(html)

    os.system("git add index.html ledger.json")
    os.system("git commit -m 'ledger update' || echo no changes")
    os.system("git push origin main")

    print("☁️ Web Updated")

# ---------------- DASHBOARD ----------------
def dashboard(db):

    os.system("clear")

    title=db["title"]
    data=db["data"]

    total=sum(i[1] for i in data)
    paid=sum(i[1] for i in data if i[2])
    bal=total-paid

    percent=int((paid/total)*100) if total>0 else 0

    print("\033[96m")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(title.center(32))
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\033[0m")

    print(f"TOTAL : ₹{total}")
    print(f"PAID  : ₹{paid}")
    print(f"BAL   : ₹{bal}")
    print()

    bar=40
    filled=int(bar*percent/100)

    print("PROGRESS")
    print("\033[92m"+"█"*filled+"\033[90m"+"░"*(bar-filled)+"\033[0m")
    print(f"{percent}%")
    print()

    print("ID  NAME                 AMT     STATUS")
    print("────────────────────────────────────────")

    for i,(name,amt,status) in enumerate(data,1):

        st="\033[92mPAID\033[0m" if status else "\033[91mPENDING\033[0m"

        print(f"{i:02}  {name:<20} {amt:<7} {st}")

# ---------------- COMMANDS ----------------

db=load_db()
args=sys.argv

if len(args)<2:
    dashboard(db)

else:

    cmd=args[1]

    if cmd=="add":

        check_auth()

        name=args[2]
        amt=int(args[3])

        db["data"].append([name,amt,False])

        save_db(db)
        update_web(db)

    elif cmd=="pay":

        check_auth()

        name=args[2]

        for p in db["data"]:
            if name.lower() in p[0].lower():
                p[2]=True
                print("Marked Paid")

        save_db(db)
        update_web(db)

    elif cmd=="delete":

        check_auth()

        name=args[2]

        db["data"]=[p for p in db["data"] if name.lower() not in p[0].lower()]

        save_db(db)
        update_web(db)

    elif cmd=="edit":

        check_auth()

        name=args[2]
        amt=int(args[3])

        for p in db["data"]:
            if name.lower() in p[0].lower():
                p[1]=amt

        save_db(db)
        update_web(db)

    elif cmd=="search":

        name=args[2]

        for p in db["data"]:
            if name.lower() in p[0].lower():
                print(p)

    elif cmd=="remind":

        print("Pending Members\n")

        for name,amt,status in db["data"]:
            if not status:
                print(f"{name} ₹{amt}")

    elif cmd=="qr":

        url=f"https://{GH_USER}.github.io/{GH_REPO}/"

        qr=qrcode.QRCode(border=2)
        qr.add_data(url)
        qr.make(fit=True)

        qr.print_ascii()

        img=qr.make_image()
        img.save("qr.png")

        print("QR Generated")

    dashboard(db)
