(function () {
    const QUESTION_TYPE_IMAGE_SET = new Set([
        'image_question_text_answers',
        'image_question_image_answers',
    ]);
    const ANSWER_TYPE_IMAGE_SET = new Set([
        'text_question_image_answers',
        'image_question_image_answers',
    ]);

    function toggleElement(element, shouldShow) {
        if (!element) {
            return;
        }
        element.style.display = shouldShow ? '' : 'none';
    }

    function updateInlineCardTitles() {
        document.querySelectorAll('.inline-related.has_original, .inline-related:not(.empty-form)').forEach((inlineForm, index) => {
            const heading = inlineForm.querySelector('h3');
            if (!heading) {
                return;
            }

            const titleText = `Cevap ${index + 1}`;
            const correctField = inlineForm.querySelector('input[id$="-is_correct"]');
            const isCorrect = Boolean(correctField && correctField.checked);

            heading.innerHTML = `
                <span class="quiz-answer-card__title">${titleText}</span>
                <span class="quiz-answer-card__badge ${isCorrect ? 'is-correct' : ''}">
                    ${isCorrect ? 'Dogru Cevap' : 'Cevap Sikki'}
                </span>
            `;
        });
    }

    function toggleQuestionImageSourceFields(showQuestionImage) {
        const sourceField = document.getElementById('id_image_source_mode');
        const questionImageUrlRow = document.querySelector('.form-row.field-image');
        const questionImageFileRow = document.querySelector('.form-row.field-image_file');
        const questionImageAltRow = document.querySelector('.form-row.field-image_alt');
        const questionImageCaptionRow = document.querySelector('.form-row.field-image_caption');
        const sourceMode = sourceField ? sourceField.value : 'url';

        toggleElement(sourceField ? sourceField.closest('.form-row') : null, showQuestionImage);
        toggleElement(questionImageAltRow, showQuestionImage);
        toggleElement(questionImageCaptionRow, showQuestionImage);
        toggleElement(questionImageUrlRow, showQuestionImage && sourceMode === 'url');
        toggleElement(questionImageFileRow, showQuestionImage && sourceMode === 'file');
    }

    function toggleInlineImageSourceFields(inlineForm, showAnswerImages) {
        if (!inlineForm) {
            return;
        }

        const sourceField = inlineForm.querySelector('select[id$="-image_source_mode"]');
        const sourceMode = sourceField ? sourceField.value : 'url';
        const sourceRow = sourceField ? sourceField.closest('.form-row') : null;
        const textRow = inlineForm.querySelector('.field-text');
        const imageUrlRow = inlineForm.querySelector('.field-image');
        const imageFileRow = inlineForm.querySelector('.field-image_file');
        const imageAltRow = inlineForm.querySelector('.field-image_alt');

        toggleElement(textRow, !showAnswerImages);
        toggleElement(sourceRow, showAnswerImages);
        toggleElement(imageUrlRow, showAnswerImages && sourceMode === 'url');
        toggleElement(imageFileRow, showAnswerImages && sourceMode === 'file');
        toggleElement(imageAltRow, showAnswerImages);
    }

    function syncQuestionAdminFields() {
        const questionTypeField = document.getElementById('id_question_type');
        if (!questionTypeField) {
            return;
        }

        const questionType = questionTypeField.value;
        const showQuestionImage = QUESTION_TYPE_IMAGE_SET.has(questionType);
        const showAnswerImages = ANSWER_TYPE_IMAGE_SET.has(questionType);

        toggleQuestionImageSourceFields(showQuestionImage);

        document.querySelectorAll('.inline-related').forEach(inlineForm => {
            toggleInlineImageSourceFields(inlineForm, showAnswerImages);
        });

        updateInlineCardTitles();
    }

    document.addEventListener('DOMContentLoaded', function () {
        const questionTypeField = document.getElementById('id_question_type');
        if (!questionTypeField) {
            return;
        }

        questionTypeField.addEventListener('change', syncQuestionAdminFields);
        document.body.addEventListener('formset:added', syncQuestionAdminFields);
        document.body.addEventListener('change', function (event) {
            if (event.target && (
                event.target.id === 'id_image_source_mode' ||
                event.target.matches('select[id$="-image_source_mode"]')
            )) {
                syncQuestionAdminFields();
            }
            if (event.target && event.target.matches('input[id$="-is_correct"]')) {
                updateInlineCardTitles();
            }
        });
        syncQuestionAdminFields();
    });
})();
