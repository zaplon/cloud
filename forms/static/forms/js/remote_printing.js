
var rp = {

  print: function(file, tray, type){
            notie.alert(1, 'Drukowanie, proszę czekać');
			$.ajax({
				type: 'GET',
				data: typeof(tray) == 'undefined' ? { file:file } : { file:file, tray: tray, type: type },
				//processData: false,
				timeout:30000,
				crossDomain: true,
				url: "http://127.0.0.1:8080",
				success: function (responseData, textStatus, jqXHR) {
					console.log(responseData); 

				},
				error: function (responseData, textStatus, errorThrown) {
				    notie.alert(3, 'Wystąpił błąd podczas drukowania');
					window.open(file);
					//showMessage('Błąd', 'Wystąpił błąd podczas drukowania', 'print-error',function(){});
				}
			})
		},
	printRecipe: function(files, ind, pos, file){
            showMessage('Drukowanie','Drukowanie, proszę czekać','printing-wait-alert', function(){}, pos);
            $.ajax({
                type: 'GET',
                data: { file:'/media/rec/'+files[ind]+'.pdf', tray:150, type:'recipe' },
                //processData: false,
                crossDomain: true,
		        timeout: 6000,
                url: "http://127.0.0.1:8080",
                success: function (responseData, textStatus, jqXHR) {
                    $('#printing-wait-alert').remove();
                    rp.markRecipe(ind,files, pos);
                },
                error: function (responseData, textStatus, errorThrown) {
                    if (SPSR_userid != 56 && SPSR_userid != 102166)
                        window.open('/media/rec/'+files[ind]+'.pdf');
                    console.log('drukuj');
                    $('#printing-wait-alert').remove();
		    //window.open('/assets/rec/'+files[ind]+'.pdf');
                    rp.markRecipe(ind,files, pos);
                    //showMessage('Błąd', 'Wystąpił błąd podczas drukowania', 'print-error',function(){},pos);
                }
            })
        },
        markRecipe: function(ind,files, pos){
            if (ind + 1 < files.length) {
                showMessage('Drukowanie', 'Włóż receptę do podajnika i kliknij Ok', 'print-instruction', rp.printRecipe, pos, args = {
                    files: files,
                    ind: ind + 1
                }, true);
            }
            else if ($('input[name="recipeType"]').val() == 2)
                if (parseInt(SPSR_usermeta.dontUseRecipeNumbers) == 0) {

                    var tid = window.setTimeout(function () {
                        $.get('useRecipeNr', {'nr': files.length}).success(function () {
                            $('span[title="Numery recept wykorzystane"]').html(parseInt($('span[title="Numery recept wykorzystane"]').html()) + files.length);
                        })
                        $('#print-instruction').remove();
                    }, 15000);


                    showMessage('Drukowanie', 'Czy oznaczyć numery recepty jako wykorzystane?<br/>(auto oznaczenie za 15 sekund)', 'print-instruction', function () {
                        console.log('yes');
                        clearTimeout(tid);
                        $.get('useRecipeNr', {'nr': files.length}).success(function () {
                            $('span[title="Numery recept wykorzystane"]').html(parseInt($('span[title="Numery recept wykorzystane"]').html()) + files.length);
                        })
                    }, pos, null, true, function(){
                        clearTimeout(tid);
                    });
                }
        }
};
