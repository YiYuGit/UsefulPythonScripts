import asyncio
from pyppeteer import launch

async def main():
    try:
        # Launch a headless Chrome instance
        browser = await launch(headless=True)
        page = await browser.newPage()

        # Navigate to the Google homepage
        await page.goto('https://www.example.com')

        # Set the PDF options
        pdf_options = {
            'path': 'printFile.pdf',
            'format': 'A4',
        }

        # Generate a PDF of the Google homepage
        await page.pdf(pdf_options)

        # Close the browser
        await browser.close()
        
        print("PDF successfully generated.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
