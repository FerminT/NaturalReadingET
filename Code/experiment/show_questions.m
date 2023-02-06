function answers = show_questions(title, stimuli_questions, mode)
    title_index   = find(strcmp({stimuli_questions.title}, title));
 
    if strcmp(mode, 'questions')
        questions = stimuli_questions(title_index).questions;
    else
        questions = stimuli_questions(title_index).words;
    end

    answers = {};
    for qindex = 1:length(questions)
        prompt   = questions(qindex);
        dlgtitle = 'Pregunta de comprensión';
        reply    = inputdlg(prompt, dlgtitle);
        answers  = [answers reply];
    end
end