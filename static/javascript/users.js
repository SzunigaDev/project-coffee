$(document).ready(function() {
  $('#usersTable').DataTable({
    responsive: true,
    language: {
      url: "/static/javascript/spanishDT.js",
    },
    initComplete: function (settings, json) {
      var api = this.api();

      // Crear selectores en el footer para Proyecto y Manzana
      api.columns([2]).every(function (colIdx) {
          var column = this;
          var select = $('<select class="form-select form-select-sm py-0"><option value="">Filtrar</option></select>')
              .appendTo($(column.footer()).empty())
              .on('change', function () {
                  var val = $.fn.dataTable.util.escapeRegex($(this).val());
                  column.search(val ? '^' + val + '$' : '', true, false).draw();
              });

          column.data().unique().sort().each(function (d, j) {
              select.append('<option value="' + d + '">' + d + '</option>');
          });
      });
    },
    dom:
      '<"row "<"col-sm-12 col-md-4"l><"col-sm-12 col-md-4 text-center"B><"col-sm-12 col-md-4 text-end"f>>' +
      '<"row"<"col-sm-12"tr>>' +
      '<"row"<"col-sm-12 col-md-7 mt-5"i><"col-sm-12 col-md-5 mt-5"p>>',
    buttons: [
      {
        extend: "excel",
        className: "rounded-0 py-0",
        exportOptions: {
          columns: ":not(:last-child)",
        },
      },
      {
        extend: "pdf",
        className: "rounded-0 py-0",
        exportOptions: {
          columns: ":not(:last-child)",
        },
      },
      {
        extend: "print",
        className: "rounded-0 py-0",
        exportOptions: {
          columns: ":not(:last-child)",
        },
      },
      {
        extend: "colvis",
        className: "rounded-0 py-0",
        columns: ":not(:last-child)" 
      },
    ],
  });
});

function viewUser(userId) {
  $.get(`/user/${userId}`, function(data) {
    const name = `${data.first_name} ${data.last_name}`; 
    $('#uName').text(name);
    $('#uBday').text(data.birthday);
    $('#uEmail').text(data.email);
    $('#uPhone').text(data.phone_number);

  });
  $('#userModalDetail').modal('show');
}

function editUser(userId) {
  $.get(`/user/${userId}`, function(data) {
    $('#edit_first_name').val(data.first_name);
    $('#edit_last_name').val(data.last_name);
    $('#edit_birthday').val(data.birthday);
    $('#edit_email').val(data.email);
    $('#edit_phone_number').val(data.phone_number);
    if (data.gender === 'Mujer') {
      $('#edit_female').prop('checked', true);
    } else if (data.gender === 'Hombre') {
      $('#edit_male').prop('checked', true);
    } else {
      $('#edit_other').prop('checked', true);
    }
    $('#userModal').modal('show');
  });
  $('#editUserForm').attr('action', `/update_user/${userId}`);
  $('#password_div').hide();
}

function saveUser() {
  $('#editUserForm').submit();
}

function deleteUser(userId) {
  $.post(`/delete_user/${userId}`, function(data) {
    location.reload();
  });

}
