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
        verbose_mode = data.get('verboseMode', False)
        
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
                image_instruction = """The first image shows the REFERENCE ANSWER (the correct solution).
The second image shows the STUDENT'S ANSWER (the response to grade).

CRITICAL INSTRUCTION: You MUST compare the student's answer (Image 2) directly against the reference answer (Image 1). Specifically check:
- Does the student's FINAL ANSWER match the reference's final answer?
- Does the student's methodology match the reference approach?
- Are the key steps from the reference present in the student's work?

If the final answer does NOT match the reference, the maximum possible score is 5/10."""
            else:
                image_instruction = "The image shows the STUDENT'S ANSWER. Grade based on the rubric and context provided."
            
            prompt = f"""You are grading a biochemistry exam question with STRICT scoring standards.

RUBRIC (how to score):
{rubric if rubric else "Use standard biochemistry grading criteria"}

ADDITIONAL CONTEXT:
{context if context else "None provided"}

{image_instruction}

SCORING RULES (APPLY STRICTLY):
1. Correct final answer required for 8-10/10 range
2. Correct final answer + correct reasoning = 9-10/10
3. Correct final answer + minor errors in reasoning = 8/10
4. Wrong final answer + near-perfect methodology = MAX 7/10
5. Wrong final answer + good methodology = MAX 5-6/10
6. Wrong final answer + flawed methodology = MAX 3-4/10
7. Wrong final answer + wrong method = 0-2/10

A "wrong final answer" means:
- Incorrect numerical value (e.g., -3 when correct answer is -1)
- Incorrect compound/term (e.g., acrylamide when correct answer is SDS)
- Missing required components of a multi-part answer
- ANY discrepancy from the reference answer (when reference is provided)

Partial credit is ONLY awarded for:
- Correct methodology applied incorrectly
- Minor calculation errors with correct approach
- Incomplete but accurate partial solutions

DO NOT deduct points for:
- Handwriting quality or neatness
- Grammar or spelling errors
- Organization or formatting of the answer
- Presentation style

Focus ONLY on the scientific accuracy and reasoning.

Please grade the student's response on a 0-10 scale with detailed feedback:
1. Score with justification (explicitly state if final answer matches reference when applicable)
2. What was done well
3. What was missing or incorrect
4. Specific suggestions for improvement

Be rigorous and consistent. Do NOT inflate scores."""
            max_tokens = 1024
        else:
            # Concise mode - optimized for speed
            if reference_image:
                image_instruction = """Image 1: REFERENCE ANSWER (correct solution)
Image 2: STUDENT'S ANSWER (to be graded)

COMPARE student's Image 2 against reference Image 1. Student's final answer MUST match reference to score above 5/10."""
            else:
                image_instruction = "The image shows the STUDENT'S ANSWER"

            prompt = f"""Grade this biochemistry question strictly.

RUBRIC: {rubric if rubric else "Standard biochemistry criteria"}
CONTEXT: {context if context else "None"}

{image_instruction}

SCORING RULES:
- Correct final answer required for 8-10/10
- Correct answer + correct work = 9-10/10
- Correct answer + minor errors = 8/10
- Wrong answer + near-perfect method = MAX 7/10
- Wrong answer + good method = MAX 5-6/10
- Wrong answer + flawed method = MAX 3-4/10
- Wrong answer + wrong method = 0-2/10

DO NOT deduct points for handwriting, grammar, spelling, or formatting. Only grade scientific accuracy and reasoning.

Format:
Score: X/10
Reasoning: [When reference provided: Does final answer match reference? Then evaluate methodology and justify score using rules above.]

Be strict and consistent."""
            max_tokens = 250
        
        # Call Claude API
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'ANTHROPIC_API_KEY environment variable not set'}), 500

        client = anthropic.Anthropic(api_key=api_key)
        
        # Build message content dynamically
        message_content = []

        # Add reference image if provided (with explicit label)
        if reference_image:
            message_content.append({
                "type": "text",
                "text": "=== REFERENCE ANSWER (CORRECT SOLUTION) - IMAGE BELOW ==="
            })
            message_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": reference_image,
                },
            })
            message_content.append({
                "type": "text",
                "text": "=== END OF REFERENCE ANSWER ===\n\n"
            })

        # Always add student image (with explicit label)
        message_content.append({
            "type": "text",
            "text": "=== STUDENT'S ANSWER (TO BE GRADED) - IMAGE BELOW ==="
        })
        message_content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": student_image,
            },
        })
        message_content.append({
            "type": "text",
            "text": "=== END OF STUDENT'S ANSWER ===\n\n"
        })

        # Add text prompt (this goes last)
        message_content.append({
            "type": "text",
            "text": prompt
        })
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=0,  # Good - keeps it consistent
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