// CKEDITOR.config.language = 'fr';
CKEDITOR.replace( 'id_concept', {
        extraPlugins: 'mathjax',
        mathJaxLib: '/static/definitions/js/MathJax/MathJax.js?config=TeX-AMS-MML_HTMLorMML',
        language: 'es',
        toolbarGroups: [
            { name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
            { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
            { name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'paragraph' ] },
            { name: 'links', groups: [ 'links' ] },
            { name: 'math', groups: [ 'mathjax' ] },
            { name: 'insert', groups: [ 'insert' ] },
            { name: 'styles', groups: [ 'styles' ] },
            { name: 'colors', groups: [ 'colors' ] },
        ],
        removeButtons: 'Save,Templates,Cut,Copy,Paste,PasteText,Redo,Undo,PasteFromWord,Print,Preview,NewPage,Find,Replace,SelectAll,Scayt,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,CopyFormatting,RemoveFormat,Subscript,Superscript,CreateDiv,BidiLtr,BidiRtl,Anchor,Flash,Smiley,SpecialChar,PageBreak,Iframe,About',
});
