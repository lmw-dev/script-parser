---
inclusion: manual
---
# Rule: Linear Issue Creation Guide

When invoked, the AI will guide the user through creating an Issue by populating the following Markdown template.

---

### **1. 🎯 Objective (Why are we doing this?)**
*(A single sentence describing the ultimate goal and the user value it provides.)*

### **2. 📝 Background & User Story**
*(Provide context. Who is this for? What problem does it solve?)*
**As a** [User Type],
**I want to** [Perform an action],
**So that I can** [Achieve a benefit].

### **3. 💡 Functional Requirements**
*(A checklist of what the feature must do.)*
- [ ] Requirement 1
- [ ] Requirement 2

### **4. 约束与技术思考 (Technical Constraints & Thoughts)**
*(Any technical limitations, specific libraries to use, or initial architectural ideas.)*
- **Must** use `[Library/Component]` for...
- **Must** follow the API design guide: `[[110-spec-api-design.mdc]]`

### **5. ✅ Acceptance Criteria (Definition of Done)**
*(A checklist of how to verify that the task is complete. This should be concrete and testable.)*
- [ ] The user can see...
- [ ] Clicking the button results in...
- [ ] The API endpoint `GET /...` returns a `200` status code with the correct payload.

### **6. 🌐 Out of Scope**
*(What we are explicitly NOT doing in this task.)*
- This task does not include...