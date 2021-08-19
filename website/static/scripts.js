 $("form[name=signup_form").submit(function(e){
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
    $.ajax({
        url: "/signup",
        type: "post",
        data: data,
        dataType: "json",
        success: function(resp){
            alert("success")
            window.location = `${window.location.origin}/login`
        },
        error: function(resp){
            alert("User Already Exists!")
        }
    })
    e.preventDefault();
})