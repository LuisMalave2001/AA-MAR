(function(){
	
"use strict"
var studentCount = 1;

function removeStudent(idStudent){
    studentCount--;
    $("#navStudent"+ idStudent).remove();
    $("#student" + idStudent).remove();
}

function addContact(){
	$(this).find("i").removeClass("fa-plus").addClass("fa-minus");
	$(this).removeClass("btn-primary").addClass("btn-danger");
	
	$(this).removeClass("add_contact");
	
	$(this).off("click");
	$(this).on("click", removeContact);
	
	// Create new contact
	var contactHtml =
	'<div class="row mt-3">'+
	'    <div class="col-5">'+
	'        <input class="form-control" name="txtContactName"'+
	'            placeholder="Skype, Whatsapp..." />'+
	'    </div>'+
	'    <div class="col-5">'+
	'        <input class="form-control" name="txtContactId"'+
	'            placeholder="phone, email, username..." />'+
	'    </div>'+
	'    <div class="col-2">'+
	'        <button type="button" class="w-100 btn btn-primary add_contact">'+
	'            <i class="fa fa-plus"></i>'+
	'        </button>'+
	'    </div>'+
	'</div>';
	$('#contacts').append(contactHtml);
	$(".add_contact").on("click", addContact);
	
}

function removeContact(){
	$(this).parent().parent().remove();
}

function addLanguage(){
	
	$(this).find("i").removeClass("fa-plus").addClass("fa-minus");
	$(this).removeClass("btn-primary").addClass("btn-danger");
	
	$(this).removeClass("add_langage");
	
	$(this).off("click");
	$(this).on("click", removeContact);
	
	var langaugeRow = 
	'<div class="col-5">'+
	'    <select class="form-control selectLanguage" name="selLanguage">'+
	'    </select>'+
	'</div>'+
	'<div class="col-5">'+
	'    <select class="form-control selectLanguageLevel" name="selLanguageLevel">'+
	'    </select>'+
	'</div>'+
	'<div class="col-2">'+
	'    <button type="button" class="w-100 btn btn-primary add_language">'+
	'        <i class="fa fa-plus"></i>'+
	'    </button>'+
	'</div>';
	
	var $languageRow = $("<div class='row mt-3'></div>");
	
	$languageRow.html(langaugeRow);

	$languageRow.find(".selectLanguage").html($("#selLanguage").html());
	$languageRow.find(".selectLanguageLevel").html($("#selLanguageLevel").html());
	
	$('#languages').append($languageRow);
	$languageRow.on("click", ".add_language", addLanguage);
}

function getStates(){
    $('#selState').html("<option value='-1'>-Select a state-</option>");
    $.ajax({
        url: '/admission/states',
        type: 'GET',
        data: { 'country_id': $('#selCountry').val()},
        success: function(data){
            $.each(JSON.parse(data), function(i, state){
                $('#selState').append('<option value="' + state.id + '">' + state.name + '</option>')
            })
        },
        error: function(){
            console.error("Un error ha ocurrido al cargar los states");
        }
    });
}

function toggleTypes(){
	
	var is_yes = this.id === "scholarship_yes"
	
	var $scholarship_type = $('input[name=scholarship_type');
	$scholarship_type.prop("disabled", !is_yes);
//	$scholarship_type.parents("fieldset").toggle(is_yes);
}

function toggleSSFilesForm(){
	var is_yes = this.id === "scholarship_considered_yes";
	
    var $files_for_ss = $('#files_for_ss');
    $files_for_ss.find("input").prop("disabled", !is_yes);
    $files_for_ss.toggle(is_yes);
}

function disable_element(event) {
    var element_id = this.dataset["toggle"];
    document.getElementById(element_id).disabled = this.checked;
}

function blockKeyboardInput(event){
	event.preventDefault();
	return false;
}

$(function(){
    $('#selCountry').on('change', getStates);
    
    $('.custom-file-input').on("change", function(){
    	var fileName = $(this)[0].files[0].name;
    	$(this).next("label").text(fileName);
    });
    
    $(".add_contact").on("click", addContact);
    $(".add_language").on("click", addLanguage);
    
    $("input[name=want_scholarship]").on("click", toggleTypes);
    $('input[name=scholarship_considered]').on("click", toggleSSFilesForm);
   
    $('.disable-element').on("change", disable_element);
  
	if ( $('[type="date"]').prop('type') != 'date' ){
		$('[type="date"]').datepicker();
	}

	$('[type="date"]').on("keydown", blockKeyboardInput);

    var $files_for_ss = $('#files_for_ss');
	$files_for_ss.find("input").prop("disabled", true);
	//alert.error("AKSD");
});
})();