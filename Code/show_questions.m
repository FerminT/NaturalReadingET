function answers = show_questions(title)
    QUESTIONS_FILE  = fullfile('..', 'stimuli_questions.mat');
    load(QUESTIONS_FILE);

    title_index = find(strcmp({stimuli_questions.title}, title));

    prompt   = cellstr(stimuli_questions(title_index).questions);
    dlgtitle = 'Preguntas de comprensión';
    dims    = [1 35];
    answers = inputdlg(prompt, dlgtitle, dims);
end