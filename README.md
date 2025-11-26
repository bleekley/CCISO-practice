# CCISO Certification Testing Engine

A comprehensive Streamlit-based web application designed for CCISO (Certified Chief Information Security Officer) exam preparation. This interactive testing engine provides both practice exam and study modes to help candidates prepare effectively for the certification.

## Features

### 📚 Two Study Modes

**Practice Exam Mode**
- Full-length practice exam with 152 questions
- Domain-weighted distribution matching the actual exam:
  - Domain 1 (Governance, Risk, and Compliance): 32 questions (21%)
  - Domain 2 (Information Security Controls and Audit Management): 30 questions (20%)
  - Domain 3 (Security Program Management and Operations): 32 questions (21%)
  - Domain 4 (Information Security Core Competencies): 29 questions (19%)
  - Domain 5 (Strategic Planning, Finance, Procurement, and Vendor Management): 29 questions (19%)
- 150-minute countdown timer with warnings
- Navigation between questions
- Comprehensive results with pass/fail (80% passing score)
- Detailed answer review with explanations

**Study Mode**
- Select specific domains to focus on
- Choose the number of questions per session
- Immediate feedback after each answer
- Correct/incorrect indicators with explanations
- Domain metadata and source excerpts for incorrect answers
- Session results with review option

### 🎯 Key Capabilities

- **Question Repository Management** - Upload and parse .txt files with questions
- **Progress Tracking** - Visual progress bars and question counters
- **Smart Navigation** - Move between questions with Previous/Next buttons
- **Results Analysis** - Detailed score breakdown and performance metrics
- **Answer Review** - Color-coded review showing your answers vs. correct answers
- **Responsive Design** - Clean, professional interface optimized for learning

## Installation

### Option 1: Streamlit Cloud (Recommended - No Installation Required)

1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click "New app"
5. Select:
   - **Repository**: `your-username/CCISO-practice`
   - **Branch**: `main` (or your preferred branch)
   - **Main file path**: `app.py`
6. Click "Deploy"
7. Your app will be live in 2-3 minutes

### Option 2: Local Installation

**Requirements:**
- Python 3.8 or higher
- pip (Python package manager)

**Steps:**

```bash
# Clone the repository
git clone https://github.com/your-username/CCISO-practice.git
cd CCISO-practice

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The app will open automatically in your default browser at `http://localhost:8501`

## Usage

### 1. Prepare Your Question File

Create a `.txt` file with questions in the following format:

```
----Question 1
Domain: Domain 1 - Governance, Risk, and Compliance
Question text: What is the primary purpose of an information security policy?
Options:
  A. To define technical configurations
  B. To establish management's direction and support for information security [CORRECT]
  C. To list all security tools
  D. To document network diagrams
Excerpt from source: Security policies establish the foundation for an organization's security program and demonstrate management commitment.

----Question 2
Domain: Domain 2 - Information Security Controls and Audit Management
Question text: Which control type is a firewall classified as?
Options:
  A. Administrative B. Physical C. Technical [CORRECT] D. Operational
Excerpt from source: Technical controls are implemented through technology and include firewalls, encryption, and access control systems.
```

**Format Requirements:**
- Each question starts with `----Question [number]`
- Domain line: `Domain: Domain [1-5] - [Domain Name]`
- Question text: `Question text: [your question]`
- Options: Can be on separate lines or single line, one must be marked `[CORRECT]`
- Excerpt: `Excerpt from source: [reference text]`

### 2. Upload Questions

1. Launch the application
2. Click "Browse files" or drag-and-drop your `.txt` file
3. The app will parse and validate your questions
4. View the domain distribution breakdown

### 3. Choose Your Mode

**Practice Exam:**
- Simulates the full CCISO exam experience
- 150-minute timer
- 152 questions across all domains
- Answer all questions or finish early
- Review results and answers at the end

**Study Mode:**
1. Select a domain (1-5)
2. Choose number of questions (or click "All Questions")
3. Click "Start Study Session"
4. Get immediate feedback after each answer
5. Review incorrect answers with explanations
6. View final results and detailed review

### 4. Review Performance

After completing an exam or study session:
- View your score and percentage
- See pass/fail status (80% required to pass)
- Click "Review Answers" to see:
  - ✅ Correct answers (green)
  - ❌ Incorrect answers (red)
  - Your answer vs. correct answer comparison
  - Domain and source information

## Question File Format Details

### Domain Mapping

- **Domain 1**: Governance, Risk, and Compliance
- **Domain 2**: Information Security Controls and Audit Management
- **Domain 3**: Security Program Management and Operations
- **Domain 4**: Information Security Core Competencies
- **Domain 5**: Strategic Planning, Finance, Procurement, and Vendor Management

### Options Format

Both formats are supported:

**Separate Lines:**
```
Options:
  A. First option
  B. Second option
  C. Third option [CORRECT]
  D. Fourth option
```

**Single Line:**
```
Options:
  A. First option B. Second option C. Third option [CORRECT] D. Fourth option
```

## Technical Details

### Built With
- **Streamlit** - Web application framework
- **Python 3.8+** - Programming language
- **Regular Expressions** - Question parsing

### File Structure
```
CCISO-practice/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── README.md          # Documentation
└── LICENSE            # License file
```

### Session State Management

The app uses Streamlit's session state to maintain:
- Question repository
- Current exam/study session
- User answers
- Timer state
- Navigation position
- Review mode state

## Deployment

### Streamlit Cloud
The app is ready for deployment on Streamlit Cloud. Simply connect your repository and the platform will automatically detect `app.py` and `requirements.txt`.

### Other Platforms
The app can be deployed on any platform supporting Python web applications:
- Heroku
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service

## Tips for Best Results

1. **Create a Large Question Bank** - The more questions you have, the better practice experience
2. **Balance Across Domains** - Ensure good coverage of all 5 domains
3. **Use Study Mode First** - Learn with immediate feedback before taking practice exams
4. **Review Incorrect Answers** - Always review to understand why you got questions wrong
5. **Time Yourself** - Use practice exam mode to simulate real exam conditions
6. **Track Progress** - Retake exams to see improvement over time

## Troubleshooting

**Questions not loading:**
- Verify your file follows the exact format shown above
- Check that each question has `[CORRECT]` marker on one option
- Ensure domain numbers are 1-5

**Timer not updating:**
- Refresh the page
- The timer auto-updates every second

**Options showing on one line:**
- This has been fixed in the latest version
- Refresh your browser or redeploy the app

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the repository maintainer

## Acknowledgments

Built for CCISO certification candidates to practice and prepare effectively for the exam.

---

**Good luck with your CCISO certification!** 🎓🔒