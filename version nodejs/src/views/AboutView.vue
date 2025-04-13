<template>
    <div id="about-page">
        <div class="about-project">
            <h1>A propos de Play'n'trade</h1>
            <p>
                Play'n'trade est une plateforme pour les passionnées de jeux de société. Grace à son marketplace et son système d'échange, il permet de faire avancer la communauté des joueurs de jeux de société.
            </p>
        </div>
        <div class="team">
            <h2>Les développeurs</h2>
            <div class="developers-row">
                <div class="developer">
                    <img src="@/assets/img/about/clement.jpg"/>
                    <h3>CLÉMENT</h3>
                    <p>ecrire un truc ici</p>
                </div>
                <div class="developer">
                    <img src="@/assets/img/about/noe.jpg"/>
                    <h3>NOÉ</h3>
                    <p>ecrire un truc ici</p>
                </div>
                <div class="developer">
                    <img src="@/assets/img/about/lucas.jpg"/>
                    <h3>LUCAS</h3>
                    <p>ecrire un truc ici</p>
                </div>

                <div class="developer">
                    <img src="@/assets/img/about/bily.jpg"/>
                    <h3 ref="billyName">BILLY</h3>
                    <p>ecrire un truc ici</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AboutPage',
    mounted() {
        const billyNameRef = this.$refs.billyName;
        let name = "BILL";
        let name2 = "Y";

        setInterval(() => {
            name += "L";
            billyNameRef.textContent = name.toUpperCase() + name2;
        }, 2000);
    },
};
</script>

<style scoped>
#about-page {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    color: var(--pnt-black);
    text-align: center;
}

.about-project {
    margin-bottom: 30px;
}

.about-project h1 {
    font-size: 28px;
    margin-bottom: 15px;
    color: var(--pnt-primary);
}

.about-project p {
    font-size: 16px;
    margin-bottom: 15px;
    line-height: 1.6;
}

.team h2 {
    font-size: 24px;
    margin-bottom: 20px;
    color: var(--pnt-primary);
}

.developers-row {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
}

.developer {
    text-align: center;
    margin: 15px;
    flex: 1 1 30%;
    max-width: 30%;
}

.developer img {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    margin-bottom: 10px;
}

.developer h3 {
    font-size: 18px;
    margin-bottom: 5px;
}

.developer p {
    font-size: 14px;
    line-height: 1.4;
}
</style>
