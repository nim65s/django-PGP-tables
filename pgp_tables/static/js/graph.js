$('#relations').html(Viz($('#graphe').html(), {
  format:'svg', engine: 'dot'
}));

$('select').change(function(){
  $('#relations').html(Viz($('#graphe').html(), {
    format:'svg',
    engine: $("select option:selected")[0].value
  }))
})
