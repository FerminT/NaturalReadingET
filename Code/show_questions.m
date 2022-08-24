function answers = show_questions(screenptr, title, stimuli_questions, stimuli_config)
    title_index = find(strcmp({stimuli_questions.title}, title));
    questions   = stimuli_questions(title_index).questions;
    questions_pos = [(stimuli_config.CX - 800) (stimuli_config.CY - 200) (stimuli_config.CX + 200) (stimuli_config.CY + 100)];

    answers = {};
    for qindex = 1:length(questions)
        current_question = [char(questions(qindex)), ' '];
        reply   = Ask(screenptr, current_question, stimuli_config.textcolor, stimuli_config.backgroundcolor, ...
            'GetChar', questions_pos, 'center', stimuli_config.fontsize);
        answers = [answers reply];
    end
end