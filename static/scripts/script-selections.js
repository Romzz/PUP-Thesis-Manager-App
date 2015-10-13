(function($) {
    function loadAllStudents(){
        // var api_url1 = document.getElementById('selected').innerHTML;
        var thesis_api = '/api/thesis/faculty';
        $.get(thesis_api, {}, function(response){
            console.log('thesis', response)
            response.data.forEach(function(thesis){
                $('.adviser').append('<option>' +thesis.name+'</option>');
                // $('option:eq(0)').after(thesis.name);
                // $('tr:eq(1)').append('<td class="yr">'+ thesis.title + '</td>');
            });
        });
    }
    function loadDepartments(){
        // var api_url1 = document.getElementById('selected').innerHTML;
        var thesis_api_dep = '/api/thesis/department';
        $.get(thesis_api_dep, {}, function(response){
            console.log('thesis', response)
            response.data.forEach(function(thesis){
                $('.department').append('<option value='+ thesis.id +'>'+ thesis.university +' '+ thesis.college +' '+thesis.name + '</option>');
            });
        });
    }
    loadAllStudents()
    loadDepartments()
})(jQuery)