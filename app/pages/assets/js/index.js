// coloca o zoom da pagina em 90%

document.body.style.zoom = "90%";

// obter o estado inicial das configuraçoes do usuario

var request = new XMLHttpRequest();
request.open("GET", `${window.location.href}/api/initial-data`, true);
request.onreadystatechange = function () {
  if (request.readyState === 4 && request.status === 200) {

    var jsonData = JSON.parse(request.responseText);
    document.querySelector("#numeroContas").selectedIndex = jsonData["numeroContas"] - 1
    document.querySelector("#email").value = jsonData["email"]
    document.querySelector("#senha").value = jsonData["senha"]
    document.querySelector("#alias").value = jsonData["alias"]
    document.querySelector("#alias").setAttribute("data-original-value" , jsonData["alias"]);

    if (jsonData["usarProxys"] === true){
      document.querySelector("#usarProxys").checked = true

    }

    if (jsonData["headersAleatorios"] === true){
      document.querySelector("#headersAleatorios").checked = true

    }

  }
};
request.send();

// checkbox "usar alias personalizado"

  const   aliasPersonalizadoCheckbox = document.getElementById("aliasPersonalizado");
  const aliasInput = document.getElementById("alias");

  aliasInput.setAttribute("data-original-value", aliasInput.value);

    aliasPersonalizadoCheckbox.addEventListener("change", function() {

    if (this.checked) {
      aliasInput.disabled = false;
      aliasInput.value = aliasInput.getAttribute("data-original-value");

    } else {

      aliasInput.disabled = true;
      aliasInput.value = aliasInput.getAttribute("data-original-value");
    }
  });

  // mostrar/esconder senha
  
const toggleSenhaButton = document.querySelector(".toggle-password");
toggleSenhaButton.addEventListener("click", function () {
  const senhaInput = document.getElementById("senha");
  const tipoAtual = senhaInput.getAttribute("type");

  if (tipoAtual === "password") {

    senhaInput.setAttribute("type", "text");
    this.classList.remove("fa-eye-slash");
    this.classList.add("fa-eye");
  } else {

    senhaInput.setAttribute("type", "password");
    this.classList.remove("fa-eye");
    this.classList.add("fa-eye-slash");
  }
});

// iniciar a operação de criar contas

$(document).ready(function() {
  const iniciarBtn = $("button[type='submit']");
  const numeroContasInput = $("#numeroContas");
  const emailInput = $("#email");
  const senhaInput = $("#senha");
  const aliasInput = $("#alias");
  const formatoInput = $("#formato");
  const headersAleatoriosCheckbox = $("#headersAleatorios");
  const usarProxysCheckbox = $("#usarProxys");
  const aliasPersonalizadoCheckbox = $("#aliasPersonalizado");

  iniciarBtn.click(function() {
    iniciarBtn.prop("disabled", true); // Desabilita o botão "Iniciar"

    const data = {
      numeroContas: numeroContasInput.val(),
      email: emailInput.val(),
      senha: senhaInput.val(),
      alias: aliasInput.val(),
      formato: formatoInput.val(),
      headersAleatorios: headersAleatoriosCheckbox.is(":checked"),
      usarProxys: usarProxysCheckbox.is(":checked"),
      aliasPersonalizado: aliasPersonalizadoCheckbox.is(":checked")
    };

    $.ajax({
      url: window.location.href + "/api/start",
      type: "POST",
      dataType: "json",
      contentType: "application/json", 
      data: JSON.stringify(data), 
      success: function(response, status, xhr) {
        if (xhr.status !== 200) {
          iniciarBtn.prop("disabled", false); 
          console.log("status code:", xhr.status);
        }
      },
      error: function(xhr, status, error) {
        iniciarBtn.prop("disabled", false); 
        console.error("Error:", error);
      }
    });
  });
});

