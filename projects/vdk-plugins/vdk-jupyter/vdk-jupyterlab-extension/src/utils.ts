

export function removeCreateJobDataFromSessionStorage(){
    sessionStorage.removeItem('create-job-name')
    sessionStorage.removeItem('create-job-team')
    sessionStorage.removeItem('create-job-rest-api-url')
    sessionStorage.removeItem('create-job-path')
    sessionStorage.removeItem('local')
    sessionStorage.removeItem('cloud')
}

// TODO: add functions for removing data for other operations, too
