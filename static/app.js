document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('url-input');
    const downloadBtn = document.getElementById('download-btn');
    const errorMsg = document.getElementById('error-msg');
    
    const inputSection = document.querySelector('.input-section');
    const progressSection = document.getElementById('progress-section');
    const resultSection = document.getElementById('result-section');
    
    const statusText = document.getElementById('status-text');
    const progressBar = document.getElementById('progress-bar');
    const progressPercent = document.getElementById('progress-percent');
    
    const resultTitle = document.getElementById('result-title');
    const downloadLink = document.getElementById('download-link');
    const resetBtn = document.getElementById('reset-btn');
    
    const metadataToggle = document.getElementById('metadata-toggle');
    const metadataSection = document.getElementById('metadata-section');
    const metaTitle = document.getElementById('meta-title');
    const metaArtist = document.getElementById('meta-artist');
    const metaAlbum = document.getElementById('meta-album');
    
    let currentTaskId = null;
    let pollInterval = null;
    
    // Toggle metadata section
    metadataToggle.addEventListener('click', () => {
        metadataSection.classList.toggle('hidden');
        metadataToggle.classList.toggle('open');
    });
    
    // YouTube URL validation
    const isValidYouTubeUrl = (url) => {
        const p = /^(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$/;
        if(url.match(p)){
            return url.match(p)[1];
        }
        return false;
    };
    
    downloadBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        
        if (!url || !isValidYouTubeUrl(url)) {
            errorMsg.style.display = 'block';
            return;
        }
        
        errorMsg.style.display = 'none';
        
        const metadata = {
            title: metaTitle.value.trim(),
            artist: metaArtist.value.trim(),
            album: metaAlbum.value.trim(),
            audioFormat: document.getElementById('audio-format').value
        };
        
        // Start process
        try {
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 处理中...';
            
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url, metadata })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                currentTaskId = data.task_id;
                showProgress();
                startPolling();
            } else {
                showError(data.error || '发生了未知错误');
            }
        } catch (error) {
            showError('无法连接到服务器');
        }
    });
    
    urlInput.addEventListener('input', () => {
        errorMsg.style.display = 'none';
    });
    
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            downloadBtn.click();
        }
    });
    
    resetBtn.addEventListener('click', () => {
        // Reset everything
        urlInput.value = '';
        currentTaskId = null;
        if (pollInterval) clearInterval(pollInterval);
        
        progressBar.style.width = '0%';
        progressPercent.innerText = '0%';
        
        inputSection.classList.remove('hidden');
        progressSection.classList.add('hidden');
        resultSection.classList.add('hidden');
        
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '提取音频';
    });
    
    function showProgress() {
        inputSection.classList.add('hidden');
        progressSection.classList.remove('hidden');
        statusText.innerText = '正在获取视频信息...';
        progressBar.style.width = '2%';
        progressPercent.innerText = '0%';
    }
    
    function showError(msg) {
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '提取音频';
        errorMsg.innerText = msg;
        errorMsg.style.display = 'block';
        
        inputSection.classList.remove('hidden');
        progressSection.classList.add('hidden');
    }
    
    function startPolling() {
        pollInterval = setInterval(async () => {
            if (!currentTaskId) return;
            
            try {
                const response = await fetch(`/api/status/${currentTaskId}`);
                const data = await response.json();
                
                if (data.status === 'downloading') {
                    statusText.innerText = '正在极速下载音频...';
                    progressBar.style.width = `${data.progress}%`;
                    progressPercent.innerText = `${data.progress.toFixed(1)}%`;
                } else if (data.status === 'processing') {
                    statusText.innerText = '正在转换格式并嵌入封面 (可能需要一点时间)...';
                    progressBar.style.width = '100%';
                    progressPercent.innerText = '100%';
                    // We add a pulsing effect during processing
                    progressBar.style.animation = 'pulse 1s infinite alternate';
                } else if (data.status === 'completed') {
                    clearInterval(pollInterval);
                    showResult(data);
                } else if (data.status === 'error') {
                    clearInterval(pollInterval);
                    showError(data.error || '下载或转换过程中出错');
                }
            } catch (error) {
                console.error("Polling error:", error);
            }
        }, 1000);
    }
    
    function showResult(data) {
        progressSection.classList.add('hidden');
        resultSection.classList.remove('hidden');
        progressBar.style.animation = ''; // remove pulse
        
        resultTitle.innerText = data.title || '提取成功';
        downloadLink.href = `/api/file/${currentTaskId}`;
    }
});
