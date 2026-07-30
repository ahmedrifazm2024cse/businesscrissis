describe('Agentverse End-to-End Workflow', () => {
  it('Loads the dashboard, launches a crisis, and verifies DAG update', () => {
    // 1. Visit presentation mode
    cy.visit('http://localhost/presentation')
    cy.contains('Live Demonstration Mode').should('be.visible')
    
    // 2. Launch crisis
    cy.contains('Launch Crisis').first().click()
    
    // 3. Verify redirection to Workflow DAG
    cy.url().should('include', '/workflow')
    
    // 4. Verify nodes turn active
    cy.get('.react-flow__node').should('have.length.greaterThan', 5)
    cy.contains('Active').should('be.visible')
  })
})
