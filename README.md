# Rasa Chatbot for Rhodes College 

This Rasa-based chatbot is designed to provide information about the various department, answering queries related to faculty specialization, course requirements, and more.

## Features

- **Faculty Specialization Inquiries**: Find out which faculty member specializes in a particular area.
- **Major Requirement Details**: Get detailed information about major requirements in Computer Science.
- **Course Guidance**: Guidance on what courses to take for a CS major.

## Installation

To run this chatbot, you need to install Rasa Open Source. Follow these steps:

1. **Install Rasa**: 
   ```bash
   pip install rasa
2. **Clone the Repository: **
    ```bash
    git clone <repository-url>
    cd <repository-directory>

4. **Train the Model**:
    ```bash
    rasa train
5. **Run the Actions Server (In a separate terminal):**:
    ```bash
    rasa run actions

6. **Start Talking to Your Bot:**:
   ```bash
   rasa shell
## Project Structure

- `data/`
  - `nlu.yml`: NLU training data for the Rasa model.
  - `stories.yml`: Sample stories representing conversation flows.
  - `rules.yml`: Rules to define deterministic behavior of the bot.
- `actions/`
  - `actions.py`: Custom actions for dynamic responses.
- `tests/`
  - `test_stories.yml`: Test stories for evaluating the bot.
- `domain.yml`: Defines the chatbot's universe, including intents, entities, actions, and responses.
- `config.yml`: Configuration for the NLU pipeline and policies.
- `endpoints.yml`: Configures external services like action server.

## Usage

- Start a conversation with a greeting like "Hello".
- Ask about faculty specializations, e.g., "Who specializes in machine learning?"
- Inquire about major requirements, e.g., "What are the CS major requirements?"

## Customization

You can customize and extend the chatbot by:

- Adding more intents and examples in `data/nlu.yml`.
- Creating new stories in `data/stories.yml`.
- Defining additional rules in `data/rules.yml`.
- Implementing more custom actions in `actions/actions.py`.

## Contributing

Contributions to this project are welcome. Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

MIT License








