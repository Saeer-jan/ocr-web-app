(function () {
  const form = document.getElementById('ocr-form');
  if (form) {
    const progressWrap = document.getElementById('progress-wrap');
    const progress = document.getElementById('progress');
    const progressText = document.getElementById('progress-text');

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = new FormData(form);
      data.set('detect_tables', form.querySelector('input[name="detect_tables"]').checked ? 'true' : 'false');
      data.set('handwriting', form.querySelector('input[name="handwriting"]').checked ? 'true' : 'false');

      progressWrap.classList.remove('hidden');
      progress.value = 5;
      progressText.textContent = 'Uploading...';

      const response = await fetch('/api/ocr', { method: 'POST', body: data });
      const payload = await response.json();
      if (!response.ok) {
        progressText.textContent = payload.error || 'Request failed';
        return;
      }

      const jobId = payload.job_id;
      const interval = setInterval(async () => {
        const pollResponse = await fetch(`/api/jobs/${jobId}`);
        const job = await pollResponse.json();
        if (!pollResponse.ok) {
          progressText.textContent = job.error || 'Job error';
          clearInterval(interval);
          return;
        }

        progress.value = job.progress || 0;
        progressText.textContent = `Status: ${job.status} (${job.progress || 0}%)`;

        if (job.status === 'completed') {
          clearInterval(interval);
          window.location.href = `/results/${jobId}`;
        }
        if (job.status === 'failed') {
          clearInterval(interval);
        }
      }, 1200);
    });
  }

  const results = document.getElementById('results');
  if (results) {
    const jobId = results.dataset.jobId;
    const content = document.getElementById('result-content');
    document.getElementById('export-json').href = `/api/export/${jobId}.json`;
    document.getElementById('export-txt').href = `/api/export/${jobId}.txt`;

    fetch(`/api/jobs/${jobId}`)
      .then((r) => r.json())
      .then((job) => {
        if (job.status !== 'completed') {
          content.textContent = 'Result is not ready yet.';
          return;
        }

        const lines = [];
        for (const file of job.result.files || []) {
          lines.push(`# ${file.file}`);
          for (const page of file.pages || []) {
            lines.push(page.text || '');
            lines.push('');
          }
        }

        content.innerHTML = `<pre>${lines.join('\n')}</pre>`;
      })
      .catch(() => {
        content.textContent = 'Unable to load result.';
      });
  }
})();
