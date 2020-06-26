
///////////////// HTML Elements //////////////////////////////////////

// Adds header above each group of profiles when using sort by
function addGroupHeaderHTML(group) {
  $('#result-list').append(
    $('<h3/>')
      .text(group['group name'])
      .addClass("mt-2 mb-2")
  );
}

// Adds profile and data to the result list
function addProfileHTML(profile) {
  // Create a row
  var container =
  $('<div/>')
    .attr('id','profile_container')
    .addClass('border pt-2 pb-2 row');
  // Create halves of the row
  var left =
  $('<div/>')
    .addClass('col-6');
  var right =
  $('<div/>')
    .addClass('col-6');
  // Add the row to the result list
  $('#result-list').append(
    container
  );
  // Add the halves to the row
  $(container).append(
    left,
    right
  );
  // Fill in the halves with the name and data
  $(left).append(
    $('<a/>')
      .attr("href","profile/" + profile['pk'].toString())
      .text(profile['first name'] + ' ' + profile['last name'])
  );
  // Add each data that was requested
  for (i=0; i<profile['data'].length; i++) {
    $(right).append(
      $('<p/>')
        .text(profile['data'][i])
    );
  }
}

// Add the filter and delete button into the list of active filters
function addFilterHTML(filter, filter_number) {
  // var filtertext = {
  //   current_site:"Site",
  //   first_city:"City",
  //   first_state:"State",
  //   first_zip:"Zip",
  //   first_street_address:"Street Address",
  //   current_role:"Current Role",
  //   all_roles:"All Roles",
  //   current_cohort:"Cohort",
  //   current_resource_team:"Resource Team",
  //   current_resource_team_role:"Resource Team Role",
  //   excurrent_training:"Completed Training",
  //   excurrent_not_training:"Incomplete Training",
  //   first_home_ownership:"Home Ownership",
  //   first_habitat_home:"Habitat Home",
  //   first_safe_home:"Safe Home",
  //   first_repair_home:"Home Needs Repair",
  //   gender:"Gender",
  //   race:"Race",
  //   last_name:"Last Name",
  //   current_role:"Current Role",
  // }
  filtertext = {};
  for (var i = 0; i < form_choices_text.length; i++) {
    filtertext[form_choices_text[i][0]] = form_choices_text[i][1];
  }
  var container =
  $("<div/>")
    .addClass("rounded border d-inline-block m-1");
  $(container).append(
    // Filter element
    $('<a/>')
      .addClass("d-inline-block")
      .text(filtertext[filter["filterby"]] + ': ' + filter["filterinput"]),
    // Trash can icon next to filter element
    $('<button/>')
      .attr("id","delete-" + filter_number.toString())
      .addClass("fas fa-times icon-btn text-small")
      .click(function() { removeFilter($(this))})
  );
  $('#filter_list').append(container);
}

// Add filtersets to the list select dropdown
function addFilterSetsHTML(filtersets) {
  $('#list_select').append(
    // disabled option that says Your Lists
    $("<option/>")
      .attr("selected","selected")
      //.attr("disabled","disabled")
      .attr("value",'') // So can be selected on deactivation of list
      .text("Your Lists")
  );
  // Add each filterset to the dropdown
  for (i=0;i<filtersets.length;i++) {
    $('#list_select').append(
      $("<option/>")
        .text(filtersets[i]["title"])
        .attr("value",'{"title": "' + filtersets[i]["title"].toString() + '", "filters": ' + filtersets[i]["filters"].toString() + '}')
    );
  }
}

// Add the correct input for a filter based on the filter by field
function addFilterInputHTML(options) {
  if (options.length) { // If there are options create a dropdown
    $("#filter_input_container").append(
      $('<select/>')
        .addClass("d-inline-block form-control m-0")
        .attr("id","filter_input")
        .change(function() {getProfiles()})
        .val('')
    );
    // disabled option that just says select
    $('#filter_input').append(
      $("<option/>")
        .attr("selected","selected")
        .attr("disabled","disabled")
        .text("Select")
    )
    // Add each option that was passed into the function
    for (i=0;i<options.length;i++) {
      $("#filter_input").append(
        $("<option/>")
          .text(options[i])
          .attr("value",options[i])
      );
    }
  // Add an input field if there were no options passed in
  } else {
    $("#filter_input_container").append(
      $('<input/>')
        .addClass("form-control")
        .attr("id","filter_input")
        .attr("placeholder","Enter Value")
        .on("keyup", function() {getProfiles()})
        .val("")
    );
  }
}

// Add filter submit button
function addFilterSubmitHTML() {
  $("#filter_submit_btn_container").append(
    $("<i/>")
      .attr("id","filter_submit")
      .addClass("fas fa-plus-circle icon-btn d-inline-block")
      .on("click", function() {addFilter();})
  );
}

// Add the input for the filterset title
function addListTitleInputHTML(title) {
  if (!title) {
    text = "Title"; // So that placeholder is displayed
  } else {
    text = title;
  }
  $("#list_title").append(
    $('<span/>')
      .addClass("expanding_size")
      .text(text),
    $('<input/>')
      .addClass("expanding_input")
      .attr("id","title_input")
      .attr("type","text")
      .attr("placeholder","Title")
      .attr("maxlength",40)
      .attr("onInput","expandTitle()")
      .attr("value", title)
      .change(function() {addFiltersetTitle($(this).val());})
  )
}

// Add the button to delete a filterset
function addListDeleteBtnHTML() {
  $("#delete_list_btn_container").append(
    $("<button/>")
      .attr("id","delete_filterset_btn")
      .addClass("far fa-trash-alt icon-btn text-small")
      .on("click", function() {deleteFilterset();})
  )
}

// Add the data type select
function addDataSelectHTML() {
  var select =
  $("<select/>")
    .addClass("form-control")
    .change(function () {getProfiles()});
  for (var i = 0; i < form_choices_text.length; i++) {
    select.append($("<option/>").val(form_choices_text[i][0]).text(form_choices_text[i][1]))
  }
  $("#data_displayed_container").append(
    select
  );
}

// Add filter submit button
function addDataDeleteBtnHTML() {
  $("#data_delete_btn_container").append(
    $("<i/>")
      .attr("id","data_delete_btn")
      .addClass("fas fa-minus-circle icon-btn d-inline-block")
      .on("click", function() {deleteDataBtn(true);})
  );
}
////////////////////////// functions ////////////////////////////////////

// filters that are saved by the user are stored here as objects containing
// filterby and filterinput
var filters = [];
// Form that contains user inputs to filter out and display profile data
var toolinputform;


// Initialize page
$(document).ready(function(){
  getProfiles();
  getUserFilterSets();
  // Add data select
  addDataSelectHTML();
  // Add filter input
  addFilterInputHTML([]);
  // Hide filter and search
  document.getElementById('profile_search_content').scrollTop = 12;
  document.getElementById('top_search_container').classList.remove('d-none');
});



// Get the profiles based on current filters and search input and add them
// to the page
function getProfiles() {
  toolinputform = collectPageData();
  // Ajax call to the backend (GetProfiles)
  $.ajax({
    url: '/members/profile/get-profiles',
    data: toolinputform,
    method: 'POST',
    success: function (data) {
      // Returned:
      // group object containing a list of profile objects
      // Profile objects contain first name, last name, pk, and data
      var groups = data.groups;
      $('#result-list').html(null); // Clear the result list
      // Loop throught the groups
      var i = 0;
      var j = groups.length;
      for (i = 0; i < j; i++) {
        var group = groups[i];
        if (group['group name'] == 'no groups'){
          // No group header
        }
        else {
          // Add a group header
          addGroupHeaderHTML(group);
        };
        // Loop through each profile and add element under the group header
        var k = 0;
        var l = group['profiles'].length
        for (k = 0; k < l; k++) {
          addProfileHTML(group['profiles'][k]);
        };
      };
    }
  });
}

// Collect the shear input, sort by, data displayed, and filters
function collectPageData() {

  // Add each data type to a list
  var data_types = [];
  $('#data_displayed_container').children().each(function() {
    data_types.push($(this).val());
  });
  // Add unsaved filter to the list of filters
  var filters_cpy = filters.slice() // Create a copy of the array
  if ($('#filter_by').val()) {
    var unsaved_filter = {"filterby": $('#filter_by').val(),
                          "filterinput": $('#filter_input').val(),
                         };
    filters_cpy.push(unsaved_filter); // Add the unsaved filter
  }
  // Stringify the two lists to be sent to backend
  data_types = JSON.stringify(data_types);
  filters_cpy = JSON.stringify(filters_cpy);
  $('#id_datatype').val(data_types);
  $('#id_filters').val(filters_cpy);
  return $('#tool_input_form').serialize();
  // var filter_by = $('#filter_by').val();
  // var filter_input = $('#filter_input').val();

  // Collect data to input to the backend

  // var filter_by = $('#filter_by').val();
  // var filter_input = $('#filter_input').val();
  // if (!filter_input) filter_input = '';
  // var search_input = $('#search_input').val();
  // var sort_by = $("#sort_by").val();
  // // Add unsaved filters to saved filters
  // var unsaved_filter = {"filterby": filter_by, "filterinput": filter_input};
  // var all_filters = filters.slice() // Create a copy of the array
  // all_filters.push(unsaved_filter); // Add the unsaved filter
  // // Add each data type to a list
  // var data_displayed = [];
  // $('#data_displayed_container').children().each(function() {
  //   data_displayed.push($(this).val());
  // });
  // // Stringify the two lists to be sent to backend
  // data_displayed = JSON.stringify(data_displayed);
  // all_filters = JSON.stringify(all_filters);
  // data = {
  //   'search_input': search_input,
  //   'sort_by': sort_by,
  //   'data_displayed': data_displayed,
  //   'filters': all_filters,
  // }
  // return data;
}



// Create the filter elements and add them to the page based on the saved
// filters
function getFilters(){
  var filter_list_element = $('#filter_list');
  filter_list_element.empty();
  // Loop through filters and add them to the page
  j = filters.length;
  for (i = 0; i < j; i++) {
    addFilterHTML(filters[i],i);
  };
};

// Add a filter to the list of active filters
function addFilter() {
  var filterBy = $('#filter_by').val(); // Get user inputs
  var filterInput = $('#filter_input').val();
  // Add to the active filters
  filters.push( {"filterby": filterBy, "filterinput": filterInput} );
  // Update the page
  getFilters();
  getProfiles();
  // Clear the filter by
  $('#filter_by').val('');
  $('#filter_input_container').html(null); // Remove the input
  addFilterInputHTML([]); // Add an input to hold the place
  // Deactivate any active lists
  $('#list_title').html(null);
  $("#delete_list_btn_container").html(null);
  $('#list_select').val(null);
  $('#filterset_create_btn_container').html(null); // Remove buttons
  $('#filter_submit_btn_container').html(null);
  // Add the create filterset button
  //addCreateFiltersetBtnHTML();
}



// Remove the active filter
function removeFilter(button) {
  filter_number = button[0].id[7]; // Obtain the filter number from the button id
  filters.splice(filter_number,1); // Delete the filter from active filters
  // Update page
  getFilters();
  getProfiles();
  // Deactivate any active lists
  $('#list_title').html(null);
  $('#delete_list_btn_container').html(null);
  $('#list_select').val(null);
}




// Get the users filtersets and fill out the list drop down
function getUserFilterSets() {
  var filterset_select_element = $("#list_select")
  filterset_select_element.html(null); // Clear the drop down
  $("#filterset_create_btn_container").html(null); // Remove create filterset
  // button
  // Retrieve the user's filtersets
  $.ajax({
    url: "/members/profile/get-filtersets",
    dataType: 'json',
    success: function (data) {
      // Data contains list of filterset objects which contain
      // a title and a list of filter objects
      addFilterSetsHTML(data.filtersets); // Add the html elements
    },
    async: false,
  });
};


// Change the filter input to the appropriate options
function getFilterInputField(filter_by) {
  $.ajax({
    url: "/members/profile/get-filterinput",
    data: {
      'filterby':filter_by,
    },
    dataType: 'json',
    success: function (data) {
      options = data.options;
    },
    async: false,
  });
  $("#filter_input_container").html(null); // Clear the input container
  $("#filter_submit_btn_container").html(null); // Clear the button container
  addFilterInputHTML(options); // Add the correct input type to the container
  addFilterSubmitHTML();
  getProfiles() // update page
}

// Adds a the current filters to a filterset and adds to users filtersets
function createFilterset() {
  $.ajax({
    url: "/members/profile/create-filterset",
    data: {
      'filters' : JSON.stringify(filters),
    },
    dataType: 'json',
    success: function (data) {
      $("#list_title").html(null); // Clear the title
      addListTitleInputHTML(null); // Add the title input to the page
      $("#delete_list_btn_container").html(null); // Clear button
      addListDeleteBtnHTML(); // Add the delete button
      $("#title_input").focus(); // Place the cursor in the input
      getUserFilterSets(); // Update page
    },
    async: false
  });
}

// Add a title to the new filterset
function addFiltersetTitle(title) {
  $.ajax({
    url: "/members/profile/add-filterset-title",
    data: {
      'filters' : JSON.stringify(filters),
      'title' : title
    },
    dataType: 'json',
    success: function (data) {
        // Update page
        getUserFilterSets();
    },
    async: false,
  });
  // Set the list select to the new title
  $("#list_select option").each(function () {
          if ($(this).html() == title) {
              $(this).attr("selected", "selected");
              return;
          }
  });
  $("#title_input").blur(); // Remove cursor from field
}

// Delete a filterset from database
function deleteFilterset() {
  $.ajax({
    url: "/members/profile/delete-filterset",
    data: {
      'filters': JSON.stringify(filters), // Send filters
      'title': $("#title_input").val(), // Send title
    },
    dataType: 'json',
    success: function (data) {
      filters = []; // Remove all filters
      getProfiles(); // Update page
      getFilters();
      getUserFilterSets();
      $("#list_title").html(null); // Clear the title
      $("#delete_list_btn_container").html(null); // Clear the button
    }
  });
}

// Add a filterset's filters to active filters
function activateFilterset(option_val) {
  // Get the filterset from the option value
  if (option_val) {
    var value = JSON.parse(option_val);
  } else {
    var value = {"title":null,"filters":[]};
  }
  title = value["title"];
  filters = value["filters"];
  // Add the title
  $("#list_title").html(null); // Clear the title
  $("#delete_list_btn_container").html(null); // Clear button
  if (option_val) { // If deselecting a list add no title
    addListTitleInputHTML(title); // Add the title input to the page
    addListDeleteBtnHTML(); // Add the delete button
  }
  // Clear existing filters
  $('#filter_by').val('');
  getFilterInputField();
  // update
  getFilters();
  getProfiles();
}

function expandTitle() {
  $('.expanding_size').text($('.expanding_input').val()); // Copy text to the span element
  if ($('.expanding_input').val() == '') { // When expanding_input is empty
    $('.expanding_size').text('Title'); // Expand to see the placeholder
  }
}

// Add the deleteDataBtn and optionally delete a data select
function deleteDataBtn(delete_select) {
  // Delete the last data select if wanted
  if (delete_select) {
    $("#data_displayed_container").children().last().remove();
  }
  $("#data_delete_btn_container").html(null); // Delete existing button
  // If there are more than one data selects add the data delete button
  if ($("#data_displayed_container > select").length > 1) {
    addDataDeleteBtnHTML();
  }
  getProfiles();
}

// Send an XML response to export the current data to an excel sheet
function exportToExcel() {
  var data = collectPageData();
  xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
       var a, today;
       if (xhttp.readyState === 4 && xhttp.status === 200) {
           a = document.createElement('a');
           a.href = window.URL.createObjectURL(xhttp.response);
           today = new Date();
           a.download = "profiles_" + today.toDateString().split(" ").join("_") + ".xlsx";
           a.style.display = 'none';
           document.body.appendChild(a);
           return a.click();
       }
   };
   xhttp.open("POST", "/members/profile/get-profiles-excel?", true);
   xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
   xhttp.responseType = 'blob';
   xhttp.send(data);
 }

/////////////// Listners to update the page //////////////////////
$('#tool_input_form').on('submit', function(event){
    event.preventDefault();
});
$("#id_searchinput").on("keyup", function(){
  getProfiles();
});

$("#filter_by").change(function() {
  getFilterInputField($(this).val()); // Add an input field
});
$("#id_sortby").change(function() {
  getProfiles();
});
$("#id_datatype").change(function() {
  getProfiles();
});
$("#list_select").change(function() {
  activateFilterset($(this).val()); // Change the active filters
});
$("#tools_btn").on("click", function() {
  $('#tool_container').toggle();
});
$("#filterset_create").on("click", function() {
  $('#filter_by').val('');
  $('#filter_input').val('');
  createFilterset(); // Create a list
  getProfiles();
});
$("#add_data_btn").on("click", function() {
  addDataSelectHTML(); // Add a select element
  deleteDataBtn(false); // Add the delete data btn
});
$("#export_excel_btn").on("click", function() {
  exportToExcel();
})
