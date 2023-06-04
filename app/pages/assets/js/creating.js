// atualizar o log com novas informações (sim , sei, seria melhor usar um websocket, mas não tive tempo)

$(document).ready(function() {
    const logArea = $("#logArea");
  
    function addLogMessage(message) {
      logArea.append("<p>" + message + "</p>");
      logArea.scrollTop(logArea[0].scrollHeight);
    }
  
    function fetchAndUpdateLog() {
      $.ajax({
        url: "http://" + window.location.host + "/api/updates",
        type: "GET",
        dataType: "json",
        success: function(response) {
          const log = response.log;
          const finish = response.finish;
  
          if (log) {
            addLogMessage(log);
          }
  
          if (finish) {
            window.location.href = "/";
          }
        },
        error: function(error) {
          //console.error("Error:", error);
        }
      });
    }
  
    setInterval(fetchAndUpdateLog, 0);
  });
  