from flask import Flask, render_template, request
from mymath import add, subtract, multiply, divide, power, mod

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None

    if request.method == "POST":
        op = request.form.get("op")
        a = request.form.get("a", "").strip()
        b = request.form.get("b", "").strip()
        c = request.form.get("c", "").strip()

        try:
            a = float(a)
            b = float(b)

            if op in ["add", "subtract", "multiply", "divide"]:
                c = float(c)
                if op == "add":
                    result = add(a, b, c)
                elif op == "subtract":
                    result = subtract(a, b, c)
                elif op == "multiply":
                    result = multiply(a, b, c)
                elif op == "divide":
                    result = divide(a, b, c)
            elif op == "power":
                result = power(a, b)
            elif op == "mod":
                result = mod(a, b)
            else:
                error = "Unknown operation."
        except Exception:
            error = "Please enter valid numbers."

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
