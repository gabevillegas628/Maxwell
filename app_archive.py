from flask import Flask, render_template, request, jsonify
import anthropic
import os
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grade', methods=['POST'])
def grade():
    try:
        data = request.json
        
        rubric = data.get('rubric', '')
        context = data.get('context', '')
        reference_image = data.get('referenceImage', '')
        student_image = data.get('studentImage', '')
        verbose_mode = data.get('verboseMode', False)  # New toggle
        
        if not reference_image or not student_image:
            return jsonify({'error': 'Both images are required'}), 400
        
        # Remove data URL prefix if present
        if reference_image.startswith('data:image'):
            reference_image = reference_image.split(',')[1]
        if student_image.startswith('data:image'):
            student_image = student_image.split(',')[1]
        
        # Build the prompt based on mode
        if verbose_mode:
            prompt = f"""You are grading a biochemistry exam question. Here is the context:

RUBRIC (how to score):
{rubric if rubric else "Use standard biochemistry grading criteria"}

ADDITIONAL CONTEXT:
{context if context else "None provided"}

The first image shows the REFERENCE ANSWER (what a perfect response looks like).
The second image shows the STUDENT'S ANSWER.

Please grade the student's response on a scale of 0-10 and provide detailed feedback including:
1. Score with justification
2. What was done well
3. What was missing or incorrect
4. Specific suggestions for improvement

Be fair but rigorous in your assessment."""
            max_tokens = 1024
        else:
            # Concise mode - optimized for speed
            prompt = f"""You are grading a biochemistry exam question. Analyze carefully against the rubric.

RUBRIC: {rubric if rubric else "Standard biochemistry criteria"}
CONTEXT: {context if context else "None"}

Image 1: REFERENCE ANSWER (correct response)
Image 2: STUDENT'S ANSWER

Provide your assessment in this EXACT format:
Score: X/10
Reasoning: [2-3 sentences explaining the score - what's correct, what's missing]

Be accurate and fair in your scoring."""
            max_tokens = 250
        
        # Call Claude API
        client = anthropic.Anthropic()
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": reference_image,
                            },
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": student_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        feedback = message.content[0].text
        
        return jsonify({
            'feedback': feedback,
            'mode': 'verbose' if verbose_mode else 'concise'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
