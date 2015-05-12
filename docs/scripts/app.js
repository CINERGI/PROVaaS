var ajaxMore = function(el){
	$(function(){
		$(document).on('click', el + ' a.more-btn', function(e){
			e.preventDefault();
			
			$this = $(this);
			$this.addClass('loading');
			
			$.get($this.attr('href') + '&ajax', function(data){
				$(el).html(data);
			})
		});
	});
}

var bundle_detail = function(zc, validation_url, metrics_url, provn){
    ZeroClipboard.config({swfPath: zc});
	var clip = new ZeroClipboard($("#provn-copy-btn"));

    clip.on( "copy", function (event) {
      var clipboard = event.clipboardData;
      clipboard.setData( "text/plain", $("#provn-repr").text() );
    });

	clip.on('aftercopy', function(client, args){
    $('.copied-message').remove();
    $('#messages').append($('<div class="message bg-success copied-message"></div>').append($('<div class="container"></div>').text('The PROV-N content has been copied to your clipboard.')));
	});

	var form_to_delete = null;
	var validated = false;

	$(function(){
		
		$('.delete_document').click(function(e){
			e.preventDefault();
			
			// Remove any previous confirmation dialogues
			$('.cloned').remove();
			
			// Show new confirmation dialogue
			var dialogue_box = $('#dummy-alert-message').clone().addClass('cloned').show();
			$('#dummy-alert-message').after(dialogue_box);
			dialogue_box.find('.dismiss').click(function(){
				$('.cloned .alert').alert('close');
			});
			
			dialogue_box.find('.proceed').click(function(){
				form_to_delete.submit()					
			});
			
			// Store form which needs to be submitted if user confirms the deletion
			form_to_delete = $(this).parents('form')[0];
		});
		
		$('#validate-btn').click(function(e){
			e.preventDefault();
			
			if (validated){
				return;
			}
			
			validated = true;
			
			var el = $('#validation-message').show();
			
			$.ajax({
				url: validation_url,
				success: function(data) {
          if (data.valid == "unknown"){
            el.find('.loading').hide();
            el.find('.result-error').show();

            el.addClass("alert-danger").removeClass('alert-info');
          } else {
            el.find('.loading').hide();
            el.find('.result-p').show();

            el.find('.result').text(data.valid ? "valid" : "invalid");
            el.addClass(data.valid ? "alert-success" : "alert-danger").removeClass('alert-info');

            el.find('a.link').attr('href', data.url)
          }
				},
				error: function(){
					el.find('.loading').hide();
					el.find('.result-error').show();
					
					el.addClass("alert-danger").removeClass('alert-info');
				}
			});
		});
	});

    $('#metrics').on('shown.bs.collapse', function () {
        $.get(metrics_url, function(data){
            $('#metrics_table').html(data);
        });
    });
}

var list_documents = function(){
	$(function(){
		$('#id_start_time_date').datepicker({
			autoclose: 'True',
		});
		$('#id_end_time_date').datepicker({
			autoclose: 'True',
		});
        $('#id_start_time_time').timepicker({
        	minuteStep: 1,
            showSeconds: true,
            showMeridian: false,
			defaultTime: '00:00:00',
		});
		$('#id_end_time_time').timepicker({
			minuteStep: 1,
            showSeconds: true,
            showMeridian: false,
			defaultTime: '23:59:59',
		});

		// Show the current search type's search box
		$('#filter-opts .accordion-body:eq({{choice}})').collapse('show');
		
		$('.accordion-toggle').click(function(){
			// When toggling a filter form accordian section, record that we
			// are querying by this attribute and send it in our form POST

			$this = $(this);
			$('#filter_choice').val($this.data('choice'))
		});
		
		var form_to_delete = null;
		
		$('.delete_document').click(function(e){
			e.preventDefault();
			
			// Remove any previous confirmation dialogues
			$('.cloned').remove();
			
			// Show new confirmation dialogue
			var dialogue_box = $('#dummy-message').clone().addClass('cloned').show();
			$('#page-header').after(dialogue_box);
			dialogue_box.find('.dismiss').click(function(){
				$('.cloned .alert').alert('close');
			});
			
			dialogue_box.find('.proceed').click(function(){
				form_to_delete.submit()					
			});
			
			// Store form which needs to be submitted if user confirms the deletion
			form_to_delete = $(this).parents('form')[0];
		});

        // Manage display of selected document options.
        var updateBox = function(selected){
            $('#selection-box').hide();
            $('.selection-count').text(selected.length);

            if (selected.length > 0){
                $('#selection-box').show();
            }
        };

        $('#selection-box .cancel').click(function(e){
            e.preventDefault();
            setSelectedDocuments({});
        });

        $('#selection-box button[name]').click(function(e){
            if (!e.isDefaultPrevented()) {
                e.preventDefault();
                $('#selection-box #btn-val').attr('name', $(this).attr('name')).val('true');
                $('#selection-box form').submit();
                setSelectedDocuments({});
            }
        });

        updateBox(selectedDocuments());

        selectedDocumentsChangeHooks.push(updateBox);
	});
}

var admin_document = function(userTags, groupTags){
	$(function(){
        var substringMatcher = function(strs) {
          return function findMatches(q, cb) {
            var matches, substringRegex;

            // an array that will be populated with substring matches
            matches = [];

            // regex used to determine if a string contains the substring `q`
            substrRegex = new RegExp(q, 'i');

            // iterate through the pool of strings and for any string that
            // contains the substring `q`, add it to the `matches` array
            $.each(strs, function(i, str) {
              if (substrRegex.test(str)) {
                // the typeahead jQuery plugin expects suggestions to a
                // JavaScript object, refer to typeahead docs for more info
                matches.push({ value: str });
              }
            });

            cb(matches);
          };
        };

		$("#perm_type_group").each(function(){
		    var group   = $(this);
		    var form    = group.parents('form').eq(0);
		    var name    = group.attr('data-toggle-name');
		    var hidden  = $('input[name="' + name + '"]', form);
		    group.find('label').each(function(){
		      var button = $(this);
		      button.click(function(){
		          hidden.val($(this).children('input').val());
		          if(hidden.val() == "user"){
                      $('#name_add').typeahead('destroy');
                      $("#name_add" ).typeahead({}, {
                          source: substringMatcher(userTags)
                      });
		          }
		          else {
                    $('#name_add').typeahead('destroy');
                    $("#name_add" ).typeahead({}, {
                        source: substringMatcher(groupTags)
                    });
		          }
		      });
		      if(button.children('input').val() == hidden.val()) {
		        button.addClass('active');
		      }
		    });
        });

        $( "#name_add" ).typeahead({}, {
            source: substringMatcher(userTags)
        });

        $('#rename').on('shown.bs.modal', function (e) {
          $('#document_name', this).focus();
        });
	})
}

var confirm = function(button, message){
	$(function(){
		var form_to_delete = null;
		
		$(button).click(function(e){
			e.preventDefault();
			
			// Remove any previous confirmation dialogues
			$('.cloned').remove();
			
			// Show new confirmation dialogue
			var dialogue_box = $(message).clone().addClass('cloned').show();
			$(message).after(dialogue_box);
			dialogue_box.find('.dismiss').click(function(){
				$('.cloned .alert').alert('close');
			});
			
			dialogue_box.find('.proceed').click(function(){
				form_to_delete.submit()					
			});
			
			// Store form which needs to be submitted if user confirms the deletion
			form_to_delete = $(this).parents('form')[0];
			console.log(form_to_delete)
		});
	});
}

var query = function(){
	$(function(){
		$('#query_box').keydown(function(e){
			if (e.ctrlKey && (e.keyCode == 13 || e.keyCode == 10)) {
				// Ctrl+Enter pressed
				e.preventDefault();
				$('#query_form').submit();
			}
		});
		
		$('#query_box').focus();
		
		$('#query_form').submit(function(e){
			e.preventDefault();
			
			$this = $(this);
			var query = $this.find('#query_box').val();
			var return_clause = query.match(/\sRETURN (.+)(\s(LIMIT|SKIP)|$)/i);
			
			if (return_clause && return_clause.length > 0){
				var return_fields = return_clause[1].split(",");
			}
			
			if (return_clause && return_clause.length > 0){
				$('#query_loading').show();
				
				$.ajax($this.attr('action'), {
					data: $this.serialize(),
					success: function(response){
						$('#query_loading').hide();
						$("#query_results").show().empty();
						$("#dummy-message").hide();
						$("#query_rows").show().html("Query produced <strong>"+response.length+"</strong> results.");
						
						var trow = $("<tr></tr>");
						$("#query_results").append(trow);
						$.each(return_fields, function(i, field){
							trow.append($("<th></th>").text($.trim(field)))
						});
						
						$.each(response, function(i, row){
							var trow = $("<tr></tr>");
							$("#query_results").append(trow);
							
							$.each(row, function(i, value){
								trow.append($("<td></td>").text(JSON.stringify(value)))
							});
						});
					},
					error: function(){
						$('#query_loading').hide();
						$("#query_results").hide();
						$("#query_rows").hide();
						$("#dummy-message").show();
					}
				});
			}
		})
	});
}

var api_help = function(){
	var hash = "";
	window.addEventListener("hashchange", function(){
		var newHash = window.location.hash.replace(/^#/,'');
		
		if (newHash.length > 0 && newHash != hash){
			$('.collapsed').hide();
			hash = newHash;
			$('.collapsed.' + hash.replace('-', '_')).show();
		}
	}, false);
	
	$(function(){
		hash = window.location.hash.replace(/^#/,'');
		
		if (hash.length > 0)
			$('.collapsed.' + hash.replace('-', '_')).show();
		
		$('.toggle_expand, .sidebar a').click(function(e){
			$('.collapsed').hide();
			
			var newHash = $(this).attr('href').replace(/^#/, '');
			
			if (newHash == hash){
				hash = "";
				e.preventDefault();
			} else {
				hash = newHash;
				$('.collapsed.' + hash.replace('-', '_')).fadeIn();
			}
		});
	});
}

$(function(){
    $.cookie.json = true;

    var selectedDocs = $.cookie('selected_documents')||{};

    $.each(selectedDocs, function(key){
        $('.document-selection[value='+key+']').prop('checked', true);
        $('.document-selection[value='+key+']').parents('.selectable-row').addClass('selected');
    });

    $.each(selectedDocumentsChangeHooks, function(idx){
        selectedDocumentsChangeHooks[idx](selectedDocuments());
    });

    $('.document-selection').change(function(){
        var selectedDocs = $.cookie('selected_documents')||{};
        var input = $(this);
        var selected = input.prop('checked');

        if (selected){
            selectedDocs[input.val()] = true;
            input.parents('.selectable-row').addClass('selected');
        } else {
            delete selectedDocs[input.val()];
            input.parents('.selectable-row').removeClass('selected');
        }

        $.cookie('selected_documents', selectedDocs, { expires: 7, path: '/' });

        var selected = selectedDocuments();

        $.each(selectedDocumentsChangeHooks, function(idx){
            selectedDocumentsChangeHooks[idx](selected);
        });
    });

    $('#select-all-btn').click(function(){
        if ($(this).is('input')){
            var select = $(this).prop('checked');
        } else {
            var select = $('.document-selection').length > $('.document-selection:checked').length;
        }

        if (select){
            $('.document-selection').prop('checked', true);
        } else {
            $('.document-selection').prop('checked', false);
        }

        var selectedDocs = $.cookie('selected_documents')||{};

        $('.document-selection').each(function(){
            if (select){
                selectedDocs[$(this).val()] = true;
            } else {
                delete selectedDocs[$(this).val()];
            }
        });

        setSelectedDocuments(selectedDocs);
    });

    $('.confirm').click(function(e){
        $this = $(this);

        if ($this.data('confirmed')){
            return true;
        }

        e.preventDefault();

        $('#confirmation_alert').remove();

        var alert = $('<div id="confirmation_alert" class="alert alert-danger"/>')
            .append($('<h4>Are you sure you want to do this?</h4>'))
            .append($('<p/>').text($this.data('confirmation')))
            .append($('<button class="btn btn-danger" style="margin-top: 10px;">').click(function(){
                $this.data('confirmed', true);
                $this.click();
            }).text('Confirm'))
            .append($('<button class="btn btn-default" style="margin-top: 10px; margin-left: 10px;">').click(function(){
                $('#confirmation_alert').remove();
            }).text('Cancel'))

        $('#page-header').after(alert);
    });
});

var setSelectedDocuments = function(selected){
    $.cookie('selected_documents', selected, { expires: 7, path: '/' });
    $('.document-selection').prop('checked', false);
    $('.document-selection').parents('.selectable-row').removeClass('selected');
    $.each(selected, function(key){
        $('.document-selection[value='+key+']').prop('checked', true);
        $('.document-selection[value='+key+']').parents('.selectable-row').addClass('selected');
    });

    $.each(selectedDocumentsChangeHooks, function(idx){
        selectedDocumentsChangeHooks[idx](selectedDocuments());
    });
};


var selectedDocumentsChangeHooks = [function(selected){
    $('.mass-form input[name=document_ids]').val(selected.join(','));
}];

var selectedDocuments = function(){
    var response = [];
    var selectedDocuments = $.cookie('selected_documents')||{};

    $.each(selectedDocuments, function(key){
        response.push(key);
    });

    return response;
}

var folder_detail = function(){
    // Drag and drop folder/document management
    $('.document-row.drag').draggable({opacity: .85, addClasses: false, revert: true,
        helper: function(){
            var selected = $('.document-row.drag input:checked').parents('.drag');
            if (selected.length === 0) {
              selected = $(this);
            }
            var container = $('<div/>').attr('id', 'draggingContainer');
            container.append(selected.clone());
            return container;
        }});
    $('.folder-row.drag').draggable({opacity: .85, addClasses: false, revert: true});

    $('.folder-row').droppable({
        tolerance: "pointer",
        hoverClass: "drop-hover",
        drop: function(e, ui){
            $droppable = $(this);
            var folder_id = $droppable.data('folder-id');

            if (ui.helper.filter('#draggingContainer').length > 0){
                // A group of documents or a single document was dragged onto this folder
                var ids = ui.helper.filter('#draggingContainer').find('.document-row').map(function(){
                    return $(this).data('document-id');
                }).get();

                $.post(folder_id != "None" ? "/store/folders/"+folder_id+"/insert" : "/store/folders/insert", {container_ids: ids.join(',')}, function(){
                    $('.document-row').each(function(){
                        // Remove elements from folder view
                        if (ids.indexOf($(this).data('document-id')) > -1) {
                            $(this).remove();
                        }
                    });
                    $droppable.find('.count').text(parseInt($droppable.find('.count').text()) + ids.length);
                });
            } else {
                if (ui.draggable.data('folder-id')){
                    // A folder was dragged on this folder
                    $.post(folder_id != "None" ? "/store/folders/"+folder_id+"/insert" : "/store/folders/insert", {f_id: ui.draggable.data('folder-id')}, function(){
                        ui.draggable.parent().remove();
                    });
                } else {
                    // A document was dragged onto this folder
                    $.post(folder_id != "None" ? "/store/folders/"+folder_id+"/insert" : "/store/folders/insert", {container_id: ui.draggable.data('document-id')}, function(){
                        ui.draggable.remove();
                    });
                }
                $droppable.find('.count').text(parseInt($droppable.find('.count').text()) + 1);
            }
        }
    });

    documents_list();
};

var public_documents_updater = function(startId){
    var latest = startId;
    var periodical = function(){
        $.get(
            "/store/api/v0/documents/",
            {
                order_by: 'id',
                id__gt: latest
            },
            function(data){
                $.each(data.objects, function(id, container){
                    var el = $('.document-row').last().hide();
                    latest = container.id;

                    el.data('document-id', container.id);
                    el.find('.document-selection').css('visibility', 'hidden');
                    el.find('.link').attr('href', el.find('.link').attr('href').replace(/\/\d+\//, '/' + container.id + '/'));
                    el.find('.name').text(container.document_name);
                    el.find('.views').text(container.views_count);
                    el.find('.owner').text(container.owner);
                    el.find('.created').text("created just now");

                    el.addClass('bg-warning').hover(function(){
                        $(this).removeClass('bg-warning');
                    });

                    $('.document-rows').prepend(el.show());
                });
            },
            "json"
        );
    }

    window.setInterval(periodical, 15000);
};

var documents_list = function(){
    // Options for selected documents
    // Manage display of selected document options.
    var updateBox = function(selected){
        $('#selection-box').css('visibility', 'hidden');
        $('.selection-count').text(selected.length);

        if (selected.length > 0){
            $('#selection-box').css('visibility', 'visible');
        }
    };

    $('#selection-box .cancel').click(function(e){
        e.preventDefault();
        setSelectedDocuments({});
    });

    $('#selection-box button[name]').click(function(e){
        if (!e.isDefaultPrevented()){
            e.preventDefault();
            $('#selection-box #btn-val').attr('name', $(this).attr('name')).val('true');
            $('#selection-box form').submit();
            setSelectedDocuments({});
        }
    });

    updateBox(selectedDocuments());

    selectedDocumentsChangeHooks.push(updateBox);
};



// AJAX CSRF things

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
