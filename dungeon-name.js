var adj1 = ["Zaklet", "Začarovan", "Čarovn", "Magick", "Proklet", "Čern", "Tajn", "Skryt", "Temn", "Černočern", "Hrůzn", "Děsiv", "Strašliv", "Hrůzostrašn", "Mrtvoln", "Mrtv", "Zapomenut", "Zapovězen", "Záhadn", "Ztracen", "Znesvěcen", "Zatracen", "Démonick", "Ďábelsk", "Gnómsk", "Vražedn", "Opuštěn"];
var noun = ["á krypta", "á hrobka", "á kobka", "ý hrob", "á pyramida", "é vězení", "é cely", "é pohřebiště", "ý labyrint", "é bludiště", "é hnízdo", "é doupě", "á nora", "á sluj", "á jeskyně", "é komnaty", "é síně", "á jáma", "é tunely", "é sídlo", "á svatyně", "ý chrám", "ý pomník", "é útočiště", "ý úkryt", "á skrýš", "á základna", "ý trezor", "á pokladnice", "á mohyla", "é katakomby", "é stoky", "á citadela", "á pevnost", "ý hrad", "á tvrz", "á líheň", "á věž", "ý důl", "á šachta"];
var noun1 = ["Krypta", "Hrobka", "Kobka", "Hrob", "Pyramida", "Pohřebiště", "Vězení", "Cely", "Labyrint", "Bludiště", "Hnízdo", "Doupě", "Nora", "Sluj", "Jeskyně", "Komnaty", "Síně", "Jáma", "Tunely", "Sídlo", "Svatyně", "Chrám", "Pomník", "Útočiště", "Úkryt", "Skrýš", "Základna", "Trezor", "Pokladnice", "Mohyla", "Katakomby", "Stoky", "Citadela", "Pevnost", "Hrad", "Tvrz", "Líheň", "Věž", "Důl", "Šachta"];
var obj = ["hrůzy", "děsu", "smrti", "zatracení", "zapomnění", "šílenství", "nekromancie", "krále goblinů", "démonů", "přízraků", "nemrtvých", "draků", "slunce", "měsíce", "moří", "oceánů", "prázdnoty", "nicoty", "strachu", "plamene", "ohně", "země", "lesa", "temnoty", "zkázy", "pavouků", "elementů", "ghúlů", "vampýrů", "prokletých", "zatracených", "hvězd", "bezbožných", "padlých andělů"];


function randint(min,max){
	var range = max - min;
	// it actually does work the other way...
	// if (range < 0) { throw new RangeError("min must be less than max"); }
	
	var rand = Math.floor(Math.random() * (range + 1));
	return min + rand;
}


function generate_text(a){
    
    var output = "";
    function print(s, end){
        if(end == null){
            end = '';
        }
        output = output + s + end;  
    }
    function input(x){

        var vysledek = output;
        output = ''
        return vysledek;
    }

    var re = "";
    var adjective;
    while (re == ""){

        var a = randint(0, 2*(adj1.length - 1));

        if (typeof adj1[a] !== "undefined") { // && typeof adjective == "undefined" 
            print(adj1[a], end = '');
            adjective = 1;
        } else{
            adjective = 0;
        }

        if (adjective == 1) {
            print(noun[randint(0, noun.length - 1)], end = ' ');
        } else{
            print(noun1[randint(0, noun1.length - 1)], end = ' ');
        }

        if (adjective == 1) {
            var o = randint(0, 1.5*(obj.length - 1));
            //var o = randint(0, (obj.length - 1));
            if (typeof obj[o] !== "undefined" ) {
                print(obj[o]);
            } else{
                //continue;
            }
        } else{
            print(obj[randint(0, obj.length - 1)]);
        }

        re = input("");
    }
return re;
}

jQuery( document ).ready(function($) {
  $('#new_name_only').click(function (e){
      e.preventDefault();
      var newName = generate_text("");
      $('#dungeon_name').val(newName);
  });
});