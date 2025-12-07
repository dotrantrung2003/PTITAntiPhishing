const featureLabels = ['Has IP instead of domain', 'Long Url', 'Url shortening service', 'Has @ symbol', 'Has "//" in Url',
                 'Has "-" in Url','Has multiple subdomains', 'Domain registration length', 'Has favicon',
                 'Has HTTP||HTTPS in domain', 'Has too many request Urls',
                 'Has too many anchor Urls', 'Has too many links to other domains',
                 'Has forms that are blank or linked to other domains',
                 'Submits information to email', 'Host name not included in Url',
                 'Uses iFrame', 'Age of domain','Has DNS records',
                 'Is in Google Index','PhishTank & StopBadware statistical report']

const featureImportances = [0.02583822, 0.06554780, 0.02955916, 0.01100053, 0.00887453, 0.08404168,
                            0.08899563, 0.03152557, 0.03728493, 0.01214850, 0.07337936, 0.22240851,
                            0.08467939, 0.09942379, 0.01081734, 0.02234941, 0.00647668, 0.03040700,
                            0.03004958, 0.01532934, 0.00986305];

function compare(a, b) {
  if (a.featureImportance < b.featureImportance) return 1;
  if (a.featureImportance > b.featureImportance) return -1;
  return 0;
}

document.addEventListener('DOMContentLoaded', function () {
  const checkPageButton = document.getElementById('checkPage');

  checkPageButton.addEventListener('click', async function () {
    $(this).attr("disabled", true);
    $(this).addClass('buttonLoader');
    $(this).text('');
    let FeaturesResult = [];

    try {
      
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.url) {
        $('#errorSection').show();
        $('#errorMessage').html('<div class="col-12 alert alert-info text-center" role="alert">You must open a website to scan it!</div>');
        $("#checkPage").removeClass('buttonLoader').text('Scan this site').attr("disabled", false);
        return;
      }

      const xhr = new XMLHttpRequest();
      const url = "http://localhost:3000/detectphishing";
      xhr.open("POST", url, true);
      xhr.setRequestHeader("Content-Type", "application/json");

      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
          const json = JSON.parse(xhr.responseText);
          if (json.hasOwnProperty('error')) {
            $('#errorSection').show();
            $('#errorMessage').empty();

            const message = (json.error === 'ERROR_NEWTAB')
              ? 'You must browse to a website in order to scan it!'
              : 'Something went wrong!';
            $("#errorMessage").append(`<div class="col-12 alert alert-info text-center" role="alert">${message}</div>`);
            $("#checkPage").removeClass('buttonLoader').text('Scan this site').attr("disabled", false);
            return;
          }

          
          $('#detailsSection').show();

          const prediction = json.prediction;
          const prob = json.probability[0][0];
          let progressBarColor;

          if (prediction === 1 && prob < 0.30) {
            $('#prediction').html('<div class="col-12 alert alert-success text-center" role="alert">We predict this site is SAFE to browse.</div>');
            $('#checkPage').attr('class', 'btn btn-success');
          }
          else if (prediction === -1 && prob >= 0.70){
            $('#prediction').html('<div class="col-12 alert alert-danger text-center" role="alert">We predict this site is NOT SAFE! We recommend closing this site.</div>');
            $('#checkPage').attr('class', 'btn btn-danger');
          }
          else {
            $('#prediction').html('<div class="col-12 alert alert-warning text-center" role="alert">We predict this site is SUSPICIOUS! Continue at your own risk.</div>');
            $('#checkPage').attr('class', 'btn btn-warning');
          }

          if (prob < 0.30) progressBarColor = '#28A745';
          else if (prob >= 0.70) progressBarColor = '#DC3545';
          else progressBarColor = '#FFC107';

          $('#progressBarContainer').empty();
          let bar = new ProgressBar.Circle(progressBarContainer, {
            color: progressBarColor,
            strokeWidth: 5,
            trailWidth: 2,
            duration: 1400,
            text: { autoStyleContainer: false },
            from: { color: progressBarColor, width: 1 },
            to: { color: progressBarColor, width: 5 },
            step: function (state, circle) {
              circle.path.setAttribute('stroke', state.color);
              circle.path.setAttribute('stroke-width', state.width);
              let value = Math.round(circle.value() * 100);
              circle.setText(value === 0 ? '0' : value + '%');
            }
          });

          bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
          bar.text.style.fontSize = '2rem';
          bar.animate(prob);

          let i = 0, j = 0;
          $('#features').empty();

          json.features[0].forEach(element => {
            FeaturesResult.push({
              featureLabel: featureLabels[i],
              featureImportance: featureImportances[i],
              featureResult: element
            });
            i++;
          });

          FeaturesResult.sort(compare);

          FeaturesResult.forEach((element, index) => {
            const animation = index % 2 === 0 ? 'animate__slideInLeft' : 'animate__slideInRight';
            const score = element.featureImportance * 100;
            let ratingScore =
              score > 20 ? "&#9733;&#9733;&#9733;&#9733;&#9733;" :
              score > 5 ? "&#9733;&#9733;&#9733;" :
              score > 2 ? "&#9733;&#9733;" : "&#9733;";

            let alertClass =
              element.featureResult == -1 ? "alert-danger" :
              element.featureResult == 1 ? "alert-dark" : "alert-warning";

            $('#features').append(`
              <div class="alert ${alertClass} col-5 animate__animated ${animation} animate__delay-1s">
                <p class="text-right"><small>${ratingScore}</small></p>
                <p class="text-center">${element.featureLabel}</p>
              </div>
            `);
          });

          $("#checkPage").removeClass('buttonLoader').text('Scan this site').attr("disabled", false);
        } else if (xhr.status === 0) {
          $('#errorSection').show();
          $('#errorMessage').html('<div class="col-12 alert alert-info text-center" role="alert">Server unavailable!</div>');
          $("#checkPage").removeClass('buttonLoader').text('Scan this site').attr("disabled", false);
        }
      };

      const data = JSON.stringify({ url: tab.url });
      xhr.send(data);
    } catch (err) {
      console.error('Error:', err);
      $('#errorSection').show();
      $('#errorMessage').html('<div class="col-12 alert alert-info text-center" role="alert">Unexpected error!</div>');
      $("#checkPage").removeClass('buttonLoader').text('Scan this site').attr("disabled", false);
    }
  });
});


document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('autoScanToggle');
  if (!toggle) return;

  chrome.storage.sync.get({ autoScanEnabled: true }, (data) => {
    toggle.checked = data.autoScanEnabled;
  });

  toggle.addEventListener('change', () => {
    chrome.storage.sync.set({ autoScanEnabled: toggle.checked });
  });
});