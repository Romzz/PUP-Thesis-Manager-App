(function($) {
    function loadAllStudents(){
        var thesis_api = '/api/thesis';
        $.get(thesis_api, {}, function(response){
            console.log('thesis', response)
            response.data.forEach(function(thesis){
                $('table tr:first').after('<tr></tr>');
                $('tr:eq(1)').append('<td class="yr">'+ thesis.year + '</td>');
                $('tr:eq(1)').append('<td class="yr">'+ thesis.title + '</td>');
                $('tr:eq(1)').append('<td class="yr">'+ thesis.abstract + '</td>');
                $('tr:eq(1)').append('<td class="yr">'+ thesis.adviser + '</td>');
                $('tr:eq(1)').append('<td class="yr">'+ thesis.member1 +', '+ thesis.member2 +', '+ thesis.member3 +', '+ thesis.member4 +', '+ thesis.member5 +'</td>');
            });
        });
    }
    loadAllStudents()
})(jQuery)