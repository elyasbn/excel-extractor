from flask import Flask, request, render_template, send_file, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Ensure the upload folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'filter':
            # Get the uploaded file
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                # Save the uploaded file
                file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
                uploaded_file.save(file_path)

                # Get the keywords from the form
                keywords = request.form['keywords'].split(',')

                # Load the Excel file into a DataFrame
                df = pd.read_excel(file_path)

                # Combine the keywords into a single regex pattern
                pattern = '|'.join([keyword.strip() for keyword in keywords])

                # Create a mask that checks each cell in the DataFrame for the pattern
                mask = df.apply(lambda row: row.astype(str).str.contains(pattern, case=False, na=False).any(), axis=1)

                # Filter the DataFrame using the mask
                filtered_df = df[mask]

                # Save the filtered data to a new file
                output_path = os.path.join(UPLOAD_FOLDER, 'filtered_data.xlsx')
                filtered_df.to_excel(output_path, index=False)

                # Return the number of filtered rows
                return jsonify({'filtered_rows': len(filtered_df)})

        elif action == 'download':
            output_path = os.path.join(UPLOAD_FOLDER, 'filtered_data.xlsx')
            return send_file(output_path, as_attachment=True, download_name='filtered_data.xlsx')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)