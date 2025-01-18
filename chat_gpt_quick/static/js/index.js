const dropZone = document.getElementById('drop-zone');
        const keywordsInput = document.getElementById('keywords');
        const submitButton = document.getElementById('submit');
        const insightDiv = document.getElementById('insight');

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragging');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragging');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragging');
            const file = e.dataTransfer.files[0];
            handleFileUpload(file);
        });

        dropZone.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.pdf';
            input.onchange = (e) => {
                const file = e.target.files[0];
                handleFileUpload(file);
            };
            input.click();
        });

        function handleFileUpload(file) {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.insight) {
                    const insight = data.insight;
        
                    // Clear previous content
                    insightDiv.innerHTML = '';
        
                    // Key Insight
                    const keyInsightElement = document.createElement('p');
                    keyInsightElement.innerHTML = `<strong>Key Insight:</strong> ${insight.key_insight}`;
                    insightDiv.appendChild(keyInsightElement);
        
                    // Actionable Insights
                    const actionableInsightsElement = document.createElement('div');
                    actionableInsightsElement.innerHTML = `<strong>Actionable Insights:</strong>`;
                    const actionableList = document.createElement('ul');
                    insight.actionable_insights.forEach(action => {
                        const listItem = document.createElement('li');
                        listItem.textContent = action;
                        actionableList.appendChild(listItem);
                    });
                    actionableInsightsElement.appendChild(actionableList);
                    insightDiv.appendChild(actionableInsightsElement);
        
                    // Target Industries
                    const targetIndustriesElement = document.createElement('div');
                    targetIndustriesElement.innerHTML = `<strong>Target Industries:</strong>`;
                    const industryList = document.createElement('ul');
                    insight.target_industries.forEach(industry => {
                        const listItem = document.createElement('li');
                        listItem.textContent = industry;
                        industryList.appendChild(listItem);
                    });
                    targetIndustriesElement.appendChild(industryList);
                    insightDiv.appendChild(targetIndustriesElement);
        
                    // Potential Impact
                    const potentialImpactElement = document.createElement('p');
                    potentialImpactElement.innerHTML = `<strong>Potential Impact:</strong> ${insight.potential_impact}`;
                    insightDiv.appendChild(potentialImpactElement);
                } else {
                    insightDiv.textContent = 'Error generating insight.';
                }
            })
            .catch(err => {
                insightDiv.textContent = 'Error: ' + err.message;
            });
        }

        submitButton.addEventListener('click', () => {
            const keywords = keywordsInput.value.trim();
            fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keywords })
            })
            .then(response => response.json())
            .then(data => {
                if (data.insight) {
                    const insight = data.insight;
        
                    // Clear previous content
                    insightDiv.innerHTML = '';
        
                    // Key Insight
                    const keyInsightElement = document.createElement('p');
                    keyInsightElement.innerHTML = `<strong>Key Insight:</strong> ${insight.key_insight}`;
                    insightDiv.appendChild(keyInsightElement);
        
                    // Actionable Insights
                    const actionableInsightsElement = document.createElement('div');
                    actionableInsightsElement.innerHTML = `<strong>Actionable Insights:</strong>`;
                    const actionableList = document.createElement('ul');
                    insight.actionable_insights.forEach(action => {
                        const listItem = document.createElement('li');
                        listItem.textContent = action;
                        actionableList.appendChild(listItem);
                    });
                    actionableInsightsElement.appendChild(actionableList);
                    insightDiv.appendChild(actionableInsightsElement);
        
                    // Target Industries
                    const targetIndustriesElement = document.createElement('div');
                    targetIndustriesElement.innerHTML = `<strong>Target Industries:</strong>`;
                    const industryList = document.createElement('ul');
                    insight.target_industries.forEach(industry => {
                        const listItem = document.createElement('li');
                        listItem.textContent = industry;
                        industryList.appendChild(listItem);
                    });
                    targetIndustriesElement.appendChild(industryList);
                    insightDiv.appendChild(targetIndustriesElement);
        
                    // Potential Impact
                    const potentialImpactElement = document.createElement('p');
                    potentialImpactElement.innerHTML = `<strong>Potential Impact:</strong> ${insight.potential_impact}`;
                    insightDiv.appendChild(potentialImpactElement);
                } else {
                    insightDiv.textContent = 'Error generating insight.';
                }
            })
            .catch(err => {
                insightDiv.textContent = 'Error: ' + err.message;
            });
        });        