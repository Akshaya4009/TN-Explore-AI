from flask import Flask, render_template, request, jsonify
import json, os, random
app=Flask(__name__)
with open(os.path.join(os.path.dirname(__file__),"data.json"),encoding="utf-8") as f: PLACES=json.load(f)
DISTRICTS=sorted({p["district"] for p in PLACES}); CATS=sorted({p["category"] for p in PLACES})
@app.route("/")
def home(): return render_template("index.html",districts=DISTRICTS,categories=CATS,total=len(PLACES))
@app.get("/api/places")
def places():
    q=request.args.get("q","").lower().strip(); d=request.args.get("district","All"); c=request.args.get("category","All")
    out=[]
    for p in PLACES:
        text=" ".join([p["name"],p["district"],p["category"],p["subcategory"],p["description"]]).lower()
        if d!="All" and p["district"]!=d: continue
        if c!="All" and p["category"]!=c: continue
        if q and q not in text: continue
        out.append(p)
    return jsonify({"count":len(out),"places":out[:100]})
@app.post("/api/recommend")
def recommend():
    x=request.get_json() or {}; d=x.get("district","All"); days=max(1,min(7,int(x.get("days",2)))); budget=int(x.get("budget",3000)); interests=set(x.get("interests",[]))
    pool=[p for p in PLACES if d=="All" or p["district"]==d]
    pool.sort(key=lambda p:(45 if p["category"] in interests else 0)+p["eco_score"]*.25+p["cultural_score"]*.2,reverse=True)
    chosen=pool[:min(15,max(6,days*4))]
    groups=[chosen[i::days] for i in range(days)]
    return jsonify({"title":f"Smart {d if d!='All' else 'Tamil Nadu'} Trip","estimated_cost":min(budget,max(900,650*days+len(chosen)*120)),
                    "eco_score":round(sum(p["eco_score"] for p in chosen)/len(chosen)),"groups":groups})
@app.post("/api/image-analyze")
def image_analyze():
    f=request.files.get("image"); fn=(f.filename if f else "").lower()
    found=next((p for p in PLACES if any(w in fn for w in p["name"].lower().split() if len(w)>3)),None)
    if not found: found=random.choice([p for p in PLACES if p["category"] in ["Nature","Heritage","Spiritual"]])
    return jsonify({"detected":found,"confidence":round(random.uniform(.82,.96),2),
                    "note":"Demo landmark recognition. Connect a trained CNN model for production."})
@app.get("/api/stats")
def stats(): return jsonify({"total":len(PLACES),"districts":len(DISTRICTS),"categories":len(CATS)})
if __name__=="__main__":
    print("Starting TN Smart Tourism...")
    print("Open http://127.0.0.1:5000")
    app.run(host="0.0.0.0",port=5000,debug=True)
