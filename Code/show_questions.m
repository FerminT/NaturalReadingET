function answers = show_questions(screenptr, title, stimuli_questions, stimuli_config, mode)
    title_index   = find(strcmp({stimuli_questions.title}, title));
    questions_pos = [(stimuli_config.CX - 800) (stimuli_config.CY - 200) (stimuli_config.CX + 200) (stimuli_config.CY + 100)];

    if strcmp(mode, 'questions')
        questions = stimuli_questions(title_index).questions;
    else
        questions = stimuli_questions(title_index).synonyms;
    end

    answers = {};
    for qindex = 1:length(questions)
        prompt   = questions(qindex);
        dlgtitle = 'Pregunta de comprensión';
        reply    = inputdlg(prompt, dlgtitle);
%         current_question = [char(questions(qindex)), ' '];
%         reply   = Ask(screenptr, current_question, stimuli_config.textcolor, stimuli_config.backgroundcolor, ...
%             'GetChar', questions_pos, 'left' , stimuli_config.fontsize);
        answers = [answers reply];
    end
end