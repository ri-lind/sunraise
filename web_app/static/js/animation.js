document.addEventListener("DOMContentLoaded", () => {
	const quoteElement = document.querySelector(".quote");
	const text = quoteElement.textContent;
	quoteElement.textContent = ""; 

	let index = 0;

	const typeLetter = () => {
			if (index < text.length) {
					quoteElement.textContent += text[index];
					index++;
					setTimeout(typeLetter, 50); 
			}
	};

	typeLetter();
});
