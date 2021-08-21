package com.vmware.taurus.service.graphql;

import com.vmware.taurus.service.graphql.model.Filter;
import graphql.GraphQLException;
import lombok.experimental.UtilityClass;
import org.springframework.data.domain.Sort;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;

@UtilityClass
public class GraphQLUtils {

   public static List<Filter> convertFilters(List<LinkedHashMap<String, String>> rawFilters) {
      List<Filter> filters = new ArrayList<>();
      if (rawFilters != null && !rawFilters.isEmpty()) {
         rawFilters.forEach(map -> {
            if (map != null && !map.isEmpty()) {
               Sort.Direction direction = map.get("sort") == null ? null : Sort.Direction.valueOf(map.get("sort"));
               filters.add(new Filter(map.get("property"), map.get("pattern"), direction));
            }
         });
      }
      return filters;
   }

   public static void validatePageInput(int pageSize, int pageNumber) {
      if (pageSize < 1 || pageSize > 100) {
         throw new GraphQLException("Page size cannot be less than 1 and greater than 100");
      }
      if (pageNumber < 1) {
         throw new GraphQLException("Page cannot be less than 1");
      }
   }

}
