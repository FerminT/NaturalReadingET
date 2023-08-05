function answers = show_questions(title, stimuli_questions, mode)
    title_index   = find(strcmp({stimuli_questions.title}, title));
 
    if strcmp(mode, 'questions')
        questions = stimuli_questions(title_index).questions;
    else
        questions = stimuli_questions(title_index).words;
    end

    answers = {};
    for qindex = 1:length(questions)
        prompt   = strcat('\fontsize{15} ', questions(qindex));
        dlgtitle = 'Pregunta de comprensión';
        dims = 1;
        definput = {''};
        opts.Interpreter = 'tex';
        reply    = inputdlg(prompt, dlgtitle, dims, definput, opts);
        answers  = [answers reply];
    end
end