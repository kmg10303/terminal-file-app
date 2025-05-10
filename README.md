# BOT FEEDER: Mu Prep Instructions

## Installation

1. **Download the Code**  
   Open [GitHub](#).  
   Click **Code** > **Download ZIP**.  
   Extract the ZIP in your `Downloads` folder.

2. **Set Up Project Directory**  
   Navigate to the extracted folder:  
   `cd ~/Downloads/terminal-file-app-main`

3. **Add Input Songs**  
   Open the `input_songs` folder.  
   Place songs inside folders named as `[Artist] - [Song Title]`.  
   You may include:  
   - Vocal only  
   - Instrumental only  
   - Vocal + Instrumental

4. **Set Up Python Environment**
   ```
   python3.11 -m venv venv
   source venv/bin/activate
   ```

5. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

## Execution

1. Ensure your terminal is in the project root:
   ```
   cd ~/Downloads/terminal-file-app-main
   ```

2. Activate virtual environment:
   ```
   source venv/bin/activate
   ```

3. Run the script:
   ```
   python3 main.py
   ```

4. View output:
   ```
   cd output
   ls
   ```

5. A summary CSV is generated in `~/Downloads`:  
   - `mu_prep_summary.csv`
