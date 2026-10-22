const form = document.getElementById("form");
const button = document.getElementById("submit");
const status = document.getElementById("status");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    button.disabled = true;
    button.textContent = "⏳ Отправляем...";
    status.textContent = "";

    const data = Object.fromEntries(new FormData(form).entries());

    try {
        const response = await fetch("/api/apply", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error("Ошибка");

        status.style.color = "#69e8a3";
        status.textContent = "✅ Заявка успешно отправлена!";
        form.reset();
    } catch (error) {
        status.style.color = "#ff7777";
        status.textContent = "❌ Ошибка отправки. Попробуйте позже.";
    } finally {
        button.disabled = false;
        button.textContent = "📨 Отправить заявку";
    }
});
