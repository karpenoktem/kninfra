#!/usr/bin/env node
const assert = require('node:assert/strict')
const puppeteer = require('puppeteer')

async function getAccData(page) {
    return await page.evaluate(() => {
        return $.getJSON("/accounts/api")
    })
}

async function toWiki(page) {
    const wiki_url = new URL("/wiki/Hoofdpagina", page.url())
    if (page.url() != wiki_url.toString()) {
        return page.goto(wiki_url.toString())
    }
}

async function getWikiUser(page) {
    await toWiki(page)
    return page.evaluate(() => {
        return document.getElementById('pt-userpage')?.textContent
    })
}

async function getWikiHeading(page) {
    await toWiki(page)
    return page.evaluate(() => {
        return document.getElementById("firstHeading").textContent
    })
}

async function testKNWebsite(browser, PARAM) {
    const page = await browser.newPage();
    await page.goto(PARAM.host);
    await Promise.all([
        page.waitForNavigation(),
        page.evaluate((PARAM) => {
            $('#loginButtonLink').click();
            $('#input-username').val(PARAM.user);
            $('#input-password').val(PARAM.pass);
            $('#input-submit').click();
        }, PARAM)])
    const user = await page.evaluate(() => {
        return $('#loginButton').text()
    })
    assert.equal(user, PARAM.user, "logged in user")
    const accData = await getAccData(page)
    assert.ok(accData.valid, "api.valid")
    assert.equal(accData.name, PARAM.user, "api.name")
    assert.equal(accData.email, PARAM.user + "@localhost", "api.email")
    // todo: assert.equal(accData.email, PARAM.user + "@karpenoktem.nl", "api.email")
    assert.equal(await getWikiUser(page), PARAM.user[0].toUpperCase() + PARAM.user.slice(1), "wiki user")
    assert.equal(await getWikiHeading(page), "Hoofdpagina", "wiki page name")
    await page.goto(PARAM.host + "/accounts/logout")
    assert.ok(!(await getAccData(page)).valid, "api logged out")
    assert.ok(!await getWikiUser(page), "wiki logged out")
    assert.equal(await getWikiHeading(page), "Fouten in rechten", "wiki loggedout permissions")
    await page.close()
}

if (process.argv.length != 5) {
    console.error("usage:", process.argv[1], "[host]", "[username]", "[password]")
    process.exit(1)
} else {
    void (async () => {
        // TODO (workaround, security): this disables the sandbox when running as root :)
        // since chrome doesn't support it
        const browser = await puppeteer.launch({
            args: process.getuid() == 0 ? ['--no-sandbox', '--disable-setuid-sandbox'] : [],
        });
        const [host, user, pass] = process.argv.slice(2)
        await testKNWebsite(browser, {
            host, user, pass
        })
        await browser.close()
    })()
}
