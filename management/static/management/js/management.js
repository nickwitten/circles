class ModelListEdit extends JqueryElement {
    constructor(id, datalist_id, form_id, parent) {
        super(id, parent)
        this.datalist_id = datalist_id;
        this.form_id = form_id;
        this.init_datalist();
        this.listeners();
    }

    init_datalist() {
        var list_elements = this.element.find('.list-item');
        var jquery_items = []
        for (var i=0; i<list_elements.length; i++ ) {
            jquery_items.push($(list_elements[i]));
        }
        this.data_list = new DataList(this.datalist_id, jquery_items, this);
        this.data_list.reset();
    }

    select_form(option) {
        if ($(option).attr("data-url")) {
            var onload_func = function() {
                this.parent.show_form();
            }
            var success_func = function(response) {
                console.log($(response));
                this.parent.hide_form();
                var data_list = $('#'+this.parent.datalist_id);
                data_list.html($(response).find("#"+this.parent.datalist_id));
                this.parent.init_datalist();
            }
            var invalid_func = function() {
                this.parent.add_back_btn();
                this.parent.listeners();
            }
            this.form = new AjaxForm(this.form_id, $(option).attr("data-url"), {'onload_func': onload_func, 'success_func': success_func, 'invalid_func': invalid_func, 'parent': this});
            this.form.load();
        }
    }

    show_form() {
        // (this) is the AjaxForm
        this.add_back_btn();
        var hidden = this.element.find(".content.hide");
        hidden.removeClass("hide");
        var full_width = hidden.css("width", "auto").width();
        hidden.width(0);
        hidden.width(full_width);
        this.listeners();
    }

    hide_form() {
        if (this.hasOwnProperty("form")) {
            this.form.element.css("width", "");
            this.form.element.addClass("hide");
        }
    }

    add_back_btn() {
        if (!$('#'+this.form_id).find('.back').length) {
            $('#'+this.form_id).prepend($('<i/>').addClass("back fas fa-times blacklink"));
        }
    }

    listeners() {
        this.element.find("*").addBack("*").off(".list-edit");
        this.element.find(".option").on("click.list-edit", {'object': this, 'func': this.select_form}, this.dispatch);
        this.element.find(".back").on("click.list-edit", {'object': this, 'func': this.hide_form}, this.dispatch);
    }
}


class AdminManage extends JqueryElement {
    constructor(id, parent) {
        super(id, parent)
        this.folders = new Folders("admin_folders", this);
        this.users = new ModelListEdit("users_content", "users", "user_form_container", this);
        this.chapters = new ModelListEdit("chapters_content", "chapters", "chapter_form_container", this);
    }
}


class SiteManage extends JqueryElement {
    constructor(id, parent) {
        super(id, parent)
    }
}


class ManagementMenu extends Menu {
    constructor(id, menu_btn_id) {
        super(id, menu_btn_id);
        this.admin = null;
        this.site = null;
        this.manage_select = new MenuSiteSelect('menu_site_select', 'radio');
        this.manage_listeners();
        this.init_admin();
    }

    init_admin() {
        this.admin = new AdminManage('main_container', this);
    }

    init_site() {
        this.site = new SiteManage('main_container', this);
    }

    trigger_update() {
        var url = url_management;
        url += "?manage=" + this.manage_select.value[0];
        history.pushState({}, '', url)
        $(window).trigger('popstate');
    }

    manage_listeners() {
        this.manage_select.element.on(":change", {'object': this, 'func': this.trigger_update}, this.dispatch);
    }
}

// Checks if there are unsaved changes before leaving
function discard_changes() {
//     var active_slide = learning_list.active_slide;
//     if (active_slide && !active_slide.changes_saved) {
//         return 'You have unsaved changes';
//     }
}


function update_page() {
    var query = parseQuery(window.location.search);
    // If there is no query, trigger an update from menu
    if (!Object.keys(query).length) {
        management_menu.trigger_update();
        return
    }

//     if (query.site) {
//         learning_list.site_select.set_value(query.site, true);
//     }
//     if (query.type) {
//         learning_list.type_select.set_value(query.type);
//     }
//     if (query.id && learning_list.slide_inds.hasOwnProperty(query.model_type)) {
//         learning_list.show_item_info(query.model_type, query.id);
//     }
}


var management_menu;
$(document).ready(function() {
    management_menu = new ManagementMenu('menu', 'menu_btn');
    $(window).bind('beforeunload', discard_changes);
    $(window).on('popstate', update_page);
    $(window).trigger('popstate');
});

