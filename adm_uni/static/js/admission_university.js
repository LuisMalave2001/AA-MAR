(function(){
	
"use strict"
var isFormValid = true;

function addContact(){
	$(this).find("i").removeClass("fa-plus").addClass("fa-minus");
	$(this).removeClass("btn-primary").addClass("btn-danger");
	
	$(this).removeClass("add_contact");
	
	$(this).off("click");
	$(this).on("click", removeContact);
	
	// Create new contact
	var contactHtml =
	'<div class="row mt-3">'+
	'    <input type="hidden" name="other_contact_id" value="-1"/>'+
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

function changeState() {
	var select_state = $('#selState');
	select_state.children("option:gt(0)").hide();
	select_state.children("option[data-country='" + $(this).val() + "']").show();

	if (select_state.children("option:selected").css("display") == "none"){
		select_state.children("option:nth(0)").prop("selected", true);
	}
}

function addLanguage(){
	
	$(this).find("i").removeClass("fa-plus").addClass("fa-minus");
	$(this).removeClass("btn-primary").addClass("btn-danger");
	
	$(this).removeClass("add_langage");
	
	$(this).off("click");
	$(this).on("click", removeContact);
	
	var langaugeRow = 
	'<div class="col-5">'+
	'    <input type="hidden" name="other_contact_id" value="-1"/>'+
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

function verifyDate(event){
	if( !moment(this.value).isValid() ){
		$('#dob_datepicker').addClass("was-validated")
 	   	this.setCustomValidity("Invalid date");
	}else{
		$('#dob_datepicker').removeClass("was-validated")
 	   	this.setCustomValidity("");
	}
}

$(function(){
    $('#selCountry').on('change', changeState);
	$('#selCountry').trigger('change');
	
    $('.custom-file-input').on("change", function(){
		var fileName = $(this)[0].files[0].name;
    	$(this).next("label").text(fileName);
    });
    
    $(".add_contact").on("click", addContact);
	$(".add_language").on("click", addLanguage);

	$('.remove_contact').on('click', removeContact);
	$('.remove_language').on('click', removeContact);
    
    $("input[name=want_scholarship]").on("click", toggleTypes);
    $('input[name=scholarship_considered]').on("click", toggleSSFilesForm);
   
    $('.disable-element').on("change", disable_element);
  
	if ( $('[type="date"]').prop('type') != 'date' ){
		$('[type="date"]').datepicker();
	}

	var $date_of_birth = $('input[name=date_of_birth]');
	var moment_dob = moment($date_of_birth.val(), 'YYYY-MM-DD');

	console.log(moment_dob.isValid());

	
	$date_of_birth.on("blur", verifyDate);
	
	$('#dob_datepicker').datetimepicker({ 
		"format": "YYYY-MM-DD",
	});
	$('#dob_datepicker').datetimepicker("viewDate", moment_dob);
	$('#dob_datepicker').datetimepicker("date", moment_dob);
	
	$('[type="date"]').on("keydown", blockKeyboardInput);
	$date_of_birth.mask('9999-99-99');
	
    var $files_for_ss = $('#files_for_ss');
	$files_for_ss.find("input").prop("disabled", true);
});
})();