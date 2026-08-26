package cn.edu.gradschool.business;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class ProgramControllerTest {
    @Autowired
    private MockMvc mvc;

    @Test
    void filtersBy408ExamSubject() throws Exception {
        mvc.perform(get("/api/v1/programs").param("examKeyword", "408"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items[0].majorCode").value("083900"));
    }

    @Test
    void savesComputerGraduateProfile() throws Exception {
        String body = """
                {"undergraduateMajor":"数据科学与大数据技术","targetMajor":"大数据技术与工程",
                 "preferredProvinces":"江苏,浙江","estimatedScore":340,"riskPreference":"BALANCED",
                 "mathFoundation":"MATH_II","professionalCourseType":"SELF_PROPOSED"}
                """;
        mvc.perform(put("/api/v1/profiles/10001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.targetMajor").value("大数据技术与工程"));
    }
}
