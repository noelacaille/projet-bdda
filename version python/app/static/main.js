document.addEventListener('DOMContentLoaded', () => {
    // Gérer l'affichage du popup
    document.body.addEventListener('submit', async (e) => {
        if (e.target.closest('.match-popup form')) {
            e.preventDefault()
            const formData = new FormData(e.target)
            
            const response = await fetch(e.target.action, {
                method: 'POST',
                body: formData
            })
            
            if (response.ok) {
                window.location.reload()
            }
        }
    })
})