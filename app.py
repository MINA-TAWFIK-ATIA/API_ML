from flask import Flask, request, jsonify
import pandas as pd
import joblib

app = Flask(__name__)

model = joblib.load("recommender_model.pkl")

features = ['Power (W)', 'Priority', 'Usage (hrs/day)', 'Budget Level',
            'Price per kWh', 'Daily kWh', 'Daily Cost (EGP)']

def recommend_and_compare_consumption_report(user_devices_df):
    X = user_devices_df[features]
    predictions = model.predict(X)
    user_devices_df["recommendation"] = predictions

    recommended_devices = user_devices_df[user_devices_df["recommendation"] == 1]

    total_consumption = user_devices_df["Daily kWh"].sum()
    recommended_consumption = recommended_devices["Daily kWh"].sum()
    consumption_difference = total_consumption - recommended_consumption

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        user_df = pd.DataFrame(data)

        missing_cols = set(features + ["Device"]) - set(user_df.columns)
        if missing_cols:
            return jsonify({"error": f"Missing columns: {missing_cols}"}), 400

        X = user_df[features]
        preds = model.predict(X)
        user_df['recommendation'] = preds

        recommended_devices = user_df[user_df['recommendation'] == 1]

        total_consumption = user_df["Daily kWh"].sum()
        recommended_consumption = recommended_devices["Daily kWh"].sum()
        consumption_difference = total_consumption - recommended_consumption

        return jsonify({
            "recommended_devices": recommended_devices["Device"].tolist(),
            "total_consumption": round(total_consumption, 2),
            "recommended_consumption": round(recommended_consumption, 2),
            "consumption_savings": round(consumption_difference, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
