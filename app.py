from flask import Flask, render_template, request, jsonify
import anthropic
import os
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
        
        if not student_image:
            return jsonify({'error': 'Student answer image is required'}), 400
        
        # Remove data URL prefix if present
        if reference_image and reference_image.startswith('data:image'):
            reference_image = reference_image.split(',')[1]
        if student_image and student_image.startswith('data:image'):
            student_image = student_image.split(',')[1]
        
        # Build the prompt based on mode
        if verbose_mode:
            if reference_image:
                image_instruction = "The first image shows the REFERENCE ANSWER (what a perfect response looks like).\nThe second image shows the STUDENT'S ANSWER."
            else:
                image_instruction = "The image shows the STUDENT'S ANSWER."
            
            prompt = f"""You are grading a biochemistry exam question. The RUBRIC is your PRIMARY authority for scoring.

RUBRIC (FOLLOW THIS STRICTLY):
{rubric if rubric else "Use standard biochemistry grading criteria"}

ADDITIONAL CONTEXT:
{context if context else "None provided"}

{image_instruction}

GRADING INSTRUCTIONS:
1. The rubric defines what is required for points - follow it exactly
2. If the rubric specifies criteria for full points, the student MUST meet those criteria
3. Fundamental errors (wrong operations, wrong formulas, wrong constants, conceptual mistakes) should result in losing most/all points for that section
4. Missing work or blank answers should receive minimal to zero points unless partial credit is explicitly warranted
5. Do NOT be lenient on major errors - if the student made a critical mistake, reflect that in the score
6. Only award points for what the student actually demonstrated correctly according to the rubric

Grade the student's response on a scale of 0-10 and provide detailed feedback including:
1. Score with justification (reference specific rubric criteria)
2. What was done well
3. What was missing or incorrect
4. Specific suggestions for improvement

Hold the student to the rubric's standards. Do not give points the student has not earned."""
            max_tokens = 1024
        else:
            # Concise mode - optimized for speed
            if reference_image:
                image_instruction = "Image 1: REFERENCE ANSWER (correct response)\nImage 2: STUDENT'S ANSWER"
            else:
                image_instruction = "The image shows the STUDENT'S ANSWER"

            prompt = f"""You are grading a biochemistry exam. The rubric is your PRIMARY scoring authority - follow it strictly.

RUBRIC (FOLLOW EXACTLY): {rubric if rubric else "Standard biochemistry criteria"}
CONTEXT: {context if context else "None"}

{image_instruction}

CRITICAL RULES:
- Award points ONLY for what the student correctly demonstrated per the rubric
- Fundamental errors (wrong operation/formula/constant/reasoning) = lose most/all points for that section
- Missing/blank answers = minimal to zero points
- Do NOT be lenient - hold student to rubric standards

Provide your assessment in this EXACT format:
Score: X/10
Reasoning: [2-3 sentences - reference rubric criteria, identify errors, justify score]

Only give points the student has earned according to the rubric."""
            max_tokens = 250
        
        # Call Claude API
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'ANTHROPIC_API_KEY environment variable not set'}), 500

        client = anthropic.Anthropic(api_key=api_key)
        
        # Build message content dynamically
        message_content = []
        
        # Add reference image if provided
        if reference_image:
            message_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": reference_image,
                },
            })
        
        # Always add student image
        message_content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": student_image,
            },
        })
        
        # Add text prompt
        message_content.append({
            "type": "text",
            "text": prompt
        })
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=0.3,  # Lower temperature for more consistent, strict grading
            messages=[
                {
                    "role": "user",
                    "content": message_content,
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
