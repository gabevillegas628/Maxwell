# AI Biochemistry Grading Assistant - Optimized Version

## 🚀 Performance Optimizations

This version includes speed optimizations while maintaining grading accuracy:

### Key Improvements

1. **Dual Mode System**
   - **Fast Mode (⚡)**: 3-5 second responses with concise feedback
   - **Detailed Mode (📝)**: 10-15 second responses with comprehensive feedback
   - Toggle between modes based on your needs

2. **Token Optimization**
   - Fast Mode: `max_tokens: 250` (optimized prompt)
   - Detailed Mode: `max_tokens: 1024` (full feedback)
   - ~60-70% speed improvement in Fast Mode

3. **Image Compression**
   - Automatic resizing to max 1920px width
   - 80% quality JPEG compression
   - Reduces 5-10MB photos to <1MB
   - Faster uploads and API processing

### How It Works

**Fast Mode** uses a streamlined prompt that:
- Still analyzes the full rubric and both images
- Provides score (X/10) with 2-3 sentence justification
- Focuses on key points: what's correct, what's missing
- Maintains accuracy while being concise

**Detailed Mode** provides:
- Full justification for the score
- What was done well
- What was missing or incorrect
- Specific suggestions for improvement

## 📊 Expected Performance

| Mode | Response Time | Token Limit | Use Case |
|------|---------------|-------------|----------|
| Fast | 3-5 seconds | 250 | Bulk grading, quick assessments |
| Detailed | 10-15 seconds | 1024 | Complex cases, student feedback |

## 🔧 Setup Instructions

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Key**
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

3. **Run the App**
   ```bash
   python app.py
   ```

4. **Open in Browser**
   ```
   http://localhost:5000
   ```

5. **Upload or Capture Images**
   - Reference Answer: Optional - provides a model answer for comparison
   - Student Answer: Required - the response to grade
   - Use Upload mode for existing images or Camera mode to capture live

### Railway Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. **Deploy on Railway**
   - Go to [Railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `Maxwell` repository
   - Railway will auto-detect the Flask app

3. **Set Environment Variable**
   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add variable: `ANTHROPIC_API_KEY` = `your-api-key-here`

4. **Deploy**
   - Railway will automatically deploy
   - Get your public URL from the Railway dashboard
   - Your app will be live at `https://your-app.railway.app`

**Note**: Railway uses the `Procfile` to run the app with Gunicorn for production.

## 💡 Usage Tips

### When to Use Fast Mode
- Grading 50+ exams
- Straightforward questions
- When you just need scores
- Time-sensitive grading periods

### When to Use Detailed Mode
- Complex, multi-part questions
- First time using a new rubric (to verify AI understands)
- When students need detailed feedback
- Borderline cases that need careful analysis

## 🧪 Testing Accuracy

To verify Fast Mode maintains accuracy:

1. Grade 10-20 responses in **Detailed Mode**
2. Re-grade the same responses in **Fast Mode**
3. Compare scores

Expected result: **95%+ agreement** on scores

Differences typically occur in:
- Borderline scores (6 vs 7)
- Partial credit edge cases
- Very nuanced responses

## 📝 FERPA Compliance Notes

- No student identifying information shown in interface
- Images sent to Anthropic API (check your institution's third-party vendor policies)
- Responses not permanently stored by the app
- Consider informing students about AI-assisted grading

## 🛠️ Customization

### Adjust Token Limits
Edit `app.py` lines 44 and 67:
```python
max_tokens = 250  # Fast mode - increase for more detail
max_tokens = 1024 # Detailed mode - decrease for speed
```

### Modify Prompts
Fast mode prompt (line 50-66 in `app.py`) can be adjusted for your specific needs.

## 🔍 Technical Details

- **Framework**: Flask 3.0
- **API**: Anthropic Claude Sonnet 4
- **Image Processing**: Client-side compression (Canvas API)
- **Frontend**: Vanilla JavaScript (no dependencies)

## 📈 Future Enhancements

Potential additions:
- Batch processing multiple exams
- CSV export of scores
- Score history/analytics
- Custom rubric templates
- Multi-language support

## 🤝 Support

For issues or questions about the grading app, refer to the Anthropic documentation at https://docs.anthropic.com
